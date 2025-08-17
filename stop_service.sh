#!/bin/bash
# Keyword Tracker API Stop Script

PID_FILE="keyword_tracker.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    echo "Stopping Keyword Tracker API (PID: $PID)..."
    
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        sleep 2
        
        # Check if process still exists
        if kill -0 $PID 2>/dev/null; then
            echo "Process still running, force killing..."
            kill -9 $PID
        fi
        
        echo "Keyword Tracker API stopped successfully"
    else
        echo "Process not found (PID: $PID)"
    fi
    
    rm $PID_FILE
else
    echo "PID file not found. Service might not be running."
    echo "Checking for any running uvicorn processes..."
    
    PIDS=$(pgrep -f "uvicorn main:app")
    if [ -n "$PIDS" ]; then
        echo "Found running uvicorn processes: $PIDS"
        echo "Stopping them..."
        pkill -f "uvicorn main:app"
        echo "Done"
    else
        echo "No uvicorn processes found"
    fi
fi