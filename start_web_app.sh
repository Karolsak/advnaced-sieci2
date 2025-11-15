#!/bin/bash
# Quick Start Script for DC Motor Web App

echo "=========================================="
echo "  DC Motor Simulator Web App Launcher"
echo "=========================================="
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not installed. Installing now..."
    pip install flask flask-cors
    echo "✅ Flask installed!"
    echo ""
fi

# Check if NumPy is installed
if ! python3 -c "import numpy" 2>/dev/null; then
    echo "⚠️  NumPy not installed. Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed!"
    echo ""
fi

echo "🚀 Starting DC Motor Simulator Web Server..."
echo ""
echo "📡 Server will be available at:"
echo "   http://localhost:5000"
echo "   http://127.0.0.1:5000"
echo ""
echo "📝 To stop the server, press Ctrl+C"
echo ""
echo "=========================================="
echo ""

# Run the web app
python3 web_app.py
