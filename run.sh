#!/bin/bash
# GlobalClaim Recovery - Quick Start Script for macOS/Linux

echo ""
echo "========================================"
echo "GlobalClaim Recovery - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

echo "[✓] Python found"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[✓] Virtual environment created"
else
    echo "[✓] Virtual environment already exists"
fi

echo ""
echo "[*] Activating virtual environment..."
source venv/bin/activate

echo "[✓] Virtual environment activated"
echo ""

# Check if requirements are installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
    echo "[✓] Dependencies installed"
else
    echo "[✓] Dependencies already installed"
fi

echo ""
echo "========================================"
echo "Starting GlobalClaim Recovery App..."
echo "========================================"
echo ""
echo "🌍 Visit: http://localhost:5000"
echo "📊 Admin: http://localhost:5000/admin/login"
echo "👤 Username: admin"
echo "🔐 Password: globalclaim2024!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
