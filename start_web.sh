#!/bin/bash
# Discord Data Scraper - Web Interface Launcher

echo "=========================================="
echo "Discord Data Scraper - Web Interface"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Create output directory
mkdir -p output

# Start the web server
echo "Starting web server..."
echo "Open your browser and navigate to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

python3 app.py
