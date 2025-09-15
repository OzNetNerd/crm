#!/bin/bash

# Find the first available port starting from a given port
find_free_port() {
    local start_port=$1
    local max_attempts=${2:-10}

    # Define unsafe ports to skip (SIP protocol ports)
    local unsafe_ports="5060 5061"

    for ((port=start_port; port<start_port+max_attempts; port++)); do
        # Skip unsafe ports
        if [[ " $unsafe_ports " =~ " $port " ]]; then
            continue
        fi

        if ! timeout 1 nc -z localhost $port 2>/dev/null; then
            echo $port
            return 0
        fi
    done

    echo "Error: No free port found in range $start_port-$((start_port+max_attempts-1))" >&2
    exit 1
}

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ -n "$CHATBOT_PID" ]; then
        kill $CHATBOT_PID 2>/dev/null
        echo "   Stopped chatbot service (PID: $CHATBOT_PID)"
    fi
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

# Get free ports (checking 30 ports from 5050-5079)
CRM_PORT=$(find_free_port 5050 30)
# CHATBOT_PORT=$(find_free_port 8020 50)

echo "🚀 Starting CRM application on http://127.0.0.1:$CRM_PORT"
# echo "🤖 Starting chatbot service on port $CHATBOT_PORT"
echo "📝 Claude Code: Use this URL to access the application"

# Create static directory if it doesn't exist
# mkdir -p chatbot/static

# Start chatbot service in background
# echo "   Starting chatbot service..."
# python3 services/chatbot/main.py --port "$CHATBOT_PORT" > chatbot.log 2>&1 &
# CHATBOT_PID=$!

# Give chatbot a moment to start
# sleep 2

# Check if chatbot started successfully
# if ! kill -0 $CHATBOT_PID 2>/dev/null; then
#     echo "❌ Failed to start chatbot service. Check chatbot.log for details."
#     exit 1
# fi

# echo "✅ Chatbot service started (PID: $CHATBOT_PID)"

# Update chat widget to use the correct chatbot port
# sed -i "s/localhost:[0-9]\{4,5\}\/ws\/chat/localhost:$CHATBOT_PORT\/ws\/chat/g" app/templates/components/chat_widget.html

# Start the Flask application (this will block)
python3 app/main.py --port "$CRM_PORT"