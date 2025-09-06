#!/bin/bash

# Find the first available port starting from 5000
find_free_port() {
    local start_port=5000
    local max_attempts=10
    
    for ((port=start_port; port<start_port+max_attempts; port++)); do
        if ! timeout 1 nc -z localhost $port 2>/dev/null; then
            echo $port
            return 0
        fi
    done
    
    echo "Error: No free port found in range $start_port-$((start_port+max_attempts-1))" >&2
    exit 1
}

# Get free port
PORT=$(find_free_port)

echo "🚀 Starting CRM application on http://127.0.0.1:$PORT"
echo "📝 Claude Code: Use this URL to access the application"

# Start the Flask application
python3 main.py --port "$PORT"