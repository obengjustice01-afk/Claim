# Global Claim Recovery - Flask App

A production-ready Flask website for GlobalClaim Recovery - helping clients recover unclaimed funds worldwide.

## Features

- **Professional UI**: Dark navy and gold theme with full-screen backgrounds
- **Responsive Design**: Mobile-friendly across all devices
- **Contact Management**: Contact form with database storage
- **Claim Submission**: File upload support for claim documents
- **Admin Panel**: Secure authentication, claims management, contact viewing
- **SEO Optimized**: Meta tags and semantic HTML
- **Floating WhatsApp Button**: Direct messaging integration
- **Smooth Animations**: Modern UX with scroll effects

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Gunicorn, Render-ready

## Project Structure

```
globalclaim/
├── app.py                  # Main Flask application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Procfile               # Heroku/Render deployment
├── render.yaml            # Render deployment config
├── instance/
│   └── database.db        # SQLite database (auto-created)
├── static/
│   ├── css/style.css      # Styling
│   ├── js/main.js         # JavaScript functionality
│   ├── images/            # Image assets
│   └── uploads/           # User uploaded files
└── templates/
    ├── base.html          # Base template
    ├── home.html          # Homepage
    ├── about.html         # About page
    ├── services.html      # Services page
    ├── how_it_works.html  # Process explanation
    ├── contact.html       # Contact form
    ├── submit_claim.html  # Claim submission
    ├── 404.html           # 404 error page
    └── admin/
        ├── login.html     # Admin login
        ├── dashboard.html # Admin dashboard
        ├── claims.html    # Claims management
        └── contacts.html  # Contact messages

## Database Models

### Admin
- id (Primary Key)
- username (Unique)
- password_hash
- created_at

### Contact
- id (Primary Key)
- name
- email
- phone
- message
- created_at

### Claim
- id (Primary Key)
- name
- email
- phone
- country
- fund_type
- amount_estimated
- file_path
- status (pending, under_review, approved, rejected)
- notes
- created_at
- updated_at

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip

### Local Development

1. **Clone and navigate to project:**
   ```bash
   cd globalclaim
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access in browser:**
   ```
   http://localhost:5000
   ```

## Admin Panel Access

- **URL**: http://localhost:5000/admin/login
- **Username**: admin
- **Password**: globalclaim2024!

### Admin Routes
- `/admin/dashboard` - Overview and statistics
- `/admin/claims` - View and manage claim submissions
- `/admin/claim/<id>` - Edit individual claim status
- `/admin/contacts` - View contact form messages
- `/admin/logout` - Logout

## Public Routes

- `/` - Homepage
- `/about` - About page
- `/services` - Services offered
- `/how-it-works` - Recovery process explanation
- `/contact` - Contact form
- `/submit-claim` - Claim submission with file upload

## Deployment

### On Render.com

1. Push to GitHub
2. Connect repository to Render
3. Deploy using `render.yaml`
4. Environment variables:
   - `FLASK_ENV`: production
   - `SECRET_KEY`: (auto-generated or set custom)

### Manual Deployment

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:create_app()
```

## Configuration

Edit `config.py` for:
- Database location
- SECRET_KEY
- Upload folder
- File size limits
- Allowed file extensions

## Contact Information

- **Email**: globalclaimrecovery@gmail.com
- **Phone**: +233257106789
- **WhatsApp**: https://wa.me/233549117378
- **Location**: Ghana (Serving Worldwide)

## Features Included

✅ Full-screen hero section with overlay
✅ Sticky navigation bar
✅ Contact form with validation
✅ Claim submission with file upload
✅ Admin authentication system
✅ Claims management interface
✅ Responsive mobile design
✅ SEO meta tags
✅ Flash messages
✅ Floating WhatsApp button
✅ Scroll-to-top button
✅ Error handling (404, 500)
✅ Database auto-initialization
✅ Production-ready code

## Security Features

- Password hashing with Werkzeug
- Session cookie security
- CSRF protection ready
- File upload validation
- SQL injection protection with ORM
- Input validation on all forms

## Performance

- Static file caching headers
- Minified CSS and JavaScript
- Database pagination
- Lazy loading for images
- Optimized database queries

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## License

This project is built for GlobalClaim Recovery. All rights reserved.

## Support

For technical issues or questions, contact the development team.
