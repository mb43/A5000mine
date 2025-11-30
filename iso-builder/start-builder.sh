#!/bin/bash
# start-builder.sh - Start the A5000mine ISO Builder web interface

set -e

echo "========================================"
echo "    A5000mine ISO Builder Startup     "
echo "========================================"
echo ""

# Check if running as root (for ISO building)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  WARNING: Not running as root"
    echo "The ISO builder requires root privileges to build ISOs."
    echo "Please run with: sudo $0"
    echo ""
    echo "The web interface will start, but ISO building will fail."
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

echo "🚀 Starting A5000mine ISO Builder..."
echo ""
if [ "$EUID" -eq 0 ]; then
    PORT=3000
else
    PORT=8000
    echo "⚠️  Running without root privileges - using port $PORT"
    echo "Note: ISO building will not work without root access"
    echo ""
fi
echo "Access the web interface at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
python3 server.py
