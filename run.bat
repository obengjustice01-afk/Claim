@echo off
REM GlobalClaim Recovery - Quick Start Script for Windows

echo.
echo ========================================
echo GlobalClaim Recovery - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [✓] Virtual environment created
) else (
    echo [✓] Virtual environment already exists
)

echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo [✓] Virtual environment activated
echo.

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    echo [✓] Dependencies installed
) else (
    echo [✓] Dependencies already installed
)

echo.
echo ========================================
echo Starting GlobalClaim Recovery App...
echo ========================================
echo.
echo 🌍 Visit: http://localhost:5000
echo 📊 Admin: http://localhost:5000/admin/login
echo 👤 Username: admin
echo 🔐 Password: globalclaim2024!
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
