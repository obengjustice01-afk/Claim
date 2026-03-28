from __future__ import annotations

import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import config

db = SQLAlchemy()
login_manager = LoginManager()

SITE = {
    "name": "GlobalClaim Recovery",
    "domain": "globalclaimrecovery.com",
    "email": "globalclaimrecovery@gmail.com",
    "phone": "+233257106789",
    "whatsapp": "https://wa.me/233549117378",
    "location": "Ghana (Serving Worldwide)",
}

COUNTRY_OPTIONS = [
    "United States",
    "United Kingdom",
    "Canada",
    "Ghana",
    "Australia",
    "United Arab Emirates",
    "South Africa",
    "Germany",
    "Singapore",
    "India",
    "Other",
]

FUND_TYPES = [
    ("bank_account", "Dormant bank account"),
    ("insurance", "Insurance payout"),
    ("inheritance", "Inheritance or estate funds"),
    ("pension", "Pension or retirement benefits"),
    ("tax_refund", "Tax refund or rebate"),
    ("government", "Government-held funds"),
    ("investment", "Investment or dividends"),
    ("other", "Other unclaimed funds"),
]

CLAIM_STATUS_LABELS = {
    "new": "New",
    "under_review": "Under review",
    "awaiting_documents": "Awaiting documents",
    "recovered": "Recovered",
    "closed": "Closed",
}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    fund_type = db.Column(db.String(80), nullable=False)
    file_path = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False, default="new")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id: str) -> Admin | None:
    return db.session.get(Admin, int(user_id))


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value or ""))


def allowed_file(filename: str, app: Flask) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_document(file_storage, app: Flask) -> str | None:
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename, app):
        raise ValueError("Please upload a PDF, DOC, DOCX, JPG, or PNG file.")

    safe_name = secure_filename(file_storage.filename)
    extension = Path(safe_name).suffix.lower()
    generated_name = (
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}{extension}"
    )
    destination = Path(app.config["UPLOAD_FOLDER"]) / generated_name
    file_storage.save(destination)
    return f"uploads/{generated_name}"


def ensure_runtime_directories(app: Flask) -> None:
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.root_path, "static", "images").mkdir(parents=True, exist_ok=True)


def bootstrap_default_admin() -> None:
    try:
        admin = db.session.scalar(select(Admin).where(Admin.username == "admin"))
        if admin is None:
            admin = Admin(username="admin")
            admin.set_password("globalclaim2024!")
            db.session.add(admin)
            db.session.commit()
    except Exception:
        # Ignore concurrent initialization errors
        db.session.rollback()


def current_config_name() -> str:
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT_NAME"):
        return "production"
    env_name = (os.getenv("FLASK_CONFIG") or os.getenv("FLASK_ENV") or "default").lower()
    if env_name.startswith("prod"):
        return "production"
    if env_name.startswith("test"):
        return "testing"
    return "development"


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name or current_config_name()])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin_login"
    login_manager.login_message = "Please log in to access the admin panel."
    login_manager.login_message_category = "warning"

    ensure_runtime_directories(app)

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        flash("Please log in to access the admin panel.", "warning")
        return redirect(url_for("admin_login"))

    @app.context_processor
    def inject_globals():
        return {
            "site": SITE,
            "current_year": datetime.utcnow().year,
            "country_options": COUNTRY_OPTIONS,
            "fund_types": FUND_TYPES,
            "fund_type_labels": dict(FUND_TYPES),
            "claim_status_labels": CLAIM_STATUS_LABELS,
        }

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def file_too_large(_error):
        flash("Uploaded files must be 10 MB or smaller.", "danger")
        return redirect(url_for("submit_claim"))

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("500.html"), 500

    @app.route("/")
    def home():
        testimonials = [
            {
                "name": "Ama Ofori",
                "location": "Accra, Ghana",
                "quote": "Their team handled the paperwork professionally and kept me informed until the funds were released.",
            },
            {
                "name": "Daniel Moore",
                "location": "London, United Kingdom",
                "quote": "GlobalClaim Recovery made an international claim feel structured, credible, and surprisingly straightforward.",
            },
            {
                "name": "Rina Patel",
                "location": "Toronto, Canada",
                "quote": "I appreciated the clear communication and secure process from the first consultation to the final payout.",
            },
        ]
        return render_template("home.html", testimonials=testimonials)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/services")
    def services():
        return render_template("services.html")

    @app.route("/how-it-works")
    def how_it_works():
        return render_template("how_it_works.html")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            message = request.form.get("message", "").strip()

            if not name or not email or not message:
                flash("Please complete all required contact fields.", "danger")
                return redirect(url_for("contact"))

            if not is_valid_email(email):
                flash("Please enter a valid email address.", "danger")
                return redirect(url_for("contact"))

            if len(message) < 15:
                flash("Your message should be at least 15 characters long.", "danger")
                return redirect(url_for("contact"))

            db.session.add(Contact(name=name, email=email, message=message))
            db.session.commit()
            flash("Your message has been received. We will reply as soon as possible.", "success")
            return redirect(url_for("contact"))

        return render_template("contact.html")

    @app.route("/submit-claim", methods=["GET", "POST"])
    def submit_claim():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            country = request.form.get("country", "").strip()
            fund_type = request.form.get("fund_type", "").strip()
            file_storage = request.files.get("document")

            if not name or not email or not country or not fund_type:
                flash("Please complete all required claim fields.", "danger")
                return redirect(url_for("submit_claim"))

            if not is_valid_email(email):
                flash("Please enter a valid email address.", "danger")
                return redirect(url_for("submit_claim"))

            if fund_type not in dict(FUND_TYPES):
                flash("Please select a valid fund type.", "danger")
                return redirect(url_for("submit_claim"))

            try:
                relative_path = save_uploaded_document(file_storage, app)
            except ValueError as exc:
                flash(str(exc), "danger")
                return redirect(url_for("submit_claim"))

            db.session.add(
                Claim(
                    name=name,
                    email=email,
                    country=country,
                    fund_type=fund_type,
                    file_path=relative_path,
                    status="new",
                )
            )
            db.session.commit()
            flash(
                "Your claim has been submitted successfully. Our team will review it and contact you shortly.",
                "success",
            )
            return redirect(url_for("submit_claim"))

        return render_template("submit_claim.html")

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Username and password are required.", "danger")
                return redirect(url_for("admin_login"))

            admin = db.session.scalar(select(Admin).where(Admin.username == username))
            if admin and admin.check_password(password):
                login_user(admin, remember=True)
                flash("Login successful.", "success")
                return redirect(url_for("admin_dashboard"))

            flash("Invalid username or password.", "danger")
            return redirect(url_for("admin_login"))

        return render_template("admin/login.html")

    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("admin_login"))

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        total_claims = db.session.scalar(select(func.count()).select_from(Claim)) or 0
        total_contacts = db.session.scalar(select(func.count()).select_from(Contact)) or 0
        recovered_claims = (
            db.session.scalar(
                select(func.count()).select_from(Claim).where(Claim.status == "recovered")
            )
            or 0
        )
        new_claims = (
            db.session.scalar(
                select(func.count()).select_from(Claim).where(Claim.status == "new")
            )
            or 0
        )

        recent_claims = db.session.scalars(
            select(Claim).order_by(Claim.created_at.desc()).limit(5)
        ).all()
        recent_contacts = db.session.scalars(
            select(Contact).order_by(Contact.created_at.desc()).limit(5)
        ).all()

        return render_template(
            "admin/dashboard.html",
            stats={
                "total_claims": total_claims,
                "new_claims": new_claims,
                "recovered_claims": recovered_claims,
                "total_contacts": total_contacts,
            },
            recent_claims=recent_claims,
            recent_contacts=recent_contacts,
        )

    @app.route("/admin/claims")
    @login_required
    def admin_claims():
        page = request.args.get("page", default=1, type=int)
        status_filter = request.args.get("status", default="all", type=str)
        statement = select(Claim).order_by(Claim.created_at.desc())

        if status_filter != "all":
            statement = statement.where(Claim.status == status_filter)

        claims = db.paginate(statement, page=page, per_page=10, error_out=False)
        return render_template(
            "admin/claims.html",
            claims=claims,
            status_filter=status_filter,
        )

    @app.post("/admin/claims/<int:claim_id>/status")
    @login_required
    def admin_update_claim_status(claim_id: int):
        claim = db.session.get(Claim, claim_id)
        if claim is None:
            abort(404)

        new_status = request.form.get("status", "").strip()
        page = request.form.get("page", default=1, type=int)
        status_filter = request.form.get("status_filter", default="all", type=str)

        if new_status not in CLAIM_STATUS_LABELS:
            flash("Invalid status selected.", "danger")
            return redirect(url_for("admin_claims", page=page, status=status_filter))

        claim.status = new_status
        db.session.commit()
        flash(f"Claim #{claim.id} updated to {CLAIM_STATUS_LABELS[new_status]}.", "success")
        return redirect(url_for("admin_claims", page=page, status=status_filter))

    @app.route("/admin/contacts")
    @login_required
    def admin_contacts():
        page = request.args.get("page", default=1, type=int)
        contacts = db.paginate(
            select(Contact).order_by(Contact.created_at.desc()),
            page=page,
            per_page=10,
            error_out=False,
        )
        return render_template("admin/contacts.html", contacts=contacts)

    with app.app_context():
        try:
            db.create_all()
            bootstrap_default_admin()
        except Exception as e:
            # Ignore "table already exists" errors from concurrent worker initialization
            if "already exists" not in str(e):
                raise

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )
