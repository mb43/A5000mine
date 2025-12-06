#!/bin/bash

# KaspaMine Income Calculator Startup Script
# This script sets up and runs the web application

echo "🚀 Starting KaspaMine Income Calculator Web App"
echo "==============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        python3 -m pip install -r requirements.txt
    fi

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your Python/pip installation."
        exit 1
    fi
else
    echo "⚠️  requirements.txt not found. Please make sure all dependencies are installed."
fi

# Check if port 5000 is available
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5000 is already in use. The app might not start properly."
    echo "   You can change the port in app.py if needed."
fi

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting web server..."
echo ""
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python3 app.py
