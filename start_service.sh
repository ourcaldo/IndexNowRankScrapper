#!/bin/bash
# Keyword Tracker API Start Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Configuration
PORT=5000
LOG_FILE="keyword_tracker.log"
PID_FILE="keyword_tracker.pid"

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if kill -0 $PID 2>/dev/null; then
        echo "Keyword Tracker API is already running (PID: $PID)"
        echo "Use ./stop_service.sh to stop it first"
        exit 1
    else
        echo "Removing stale PID file..."
        rm $PID_FILE
    fi
fi

# Start the service
echo "Starting Keyword Tracker API..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 > $LOG_FILE 2>&1 &
PID=$!

# Save PID
echo $PID > $PID_FILE

echo "Keyword Tracker API started successfully!"
echo "Port: $PORT"
echo "PID: $PID"
echo "Log file: $LOG_FILE"
echo ""
echo "Test with: curl -H 'X-API-Key: your_api_key' -H 'Host: yourdomain.com' http://localhost:$PORT/health"
echo ""
echo "Use ./stop_service.sh to stop the service"