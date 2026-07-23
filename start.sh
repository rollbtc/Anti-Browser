#!/bin/bash
# Launcher for SimpleBrowser 3.0 Web App

cd "$(dirname "$0")"

echo "=========================================="
echo "  SimpleBrowser 3.0 - Web Edition"
echo "=========================================="
echo ""

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "Starting web server..."
echo "Opening browser automatically..."
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the web server in background
python3 webapp.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Open browser automatically
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
else
    echo "Please open http://localhost:5000 in your browser"
fi

echo "Browser opened. Server is running (PID: $SERVER_PID)."
echo ""

# Wait for server process
wait $SERVER_PID
