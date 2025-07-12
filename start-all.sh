#!/bin/bash

echo "Starting Splitwise MCP Bot..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to open terminal window
open_terminal() {
    local title="$1"
    local command="$2"
    local dir="$3"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - open new Terminal window
        osascript -e "tell application \"Terminal\" to do script \"cd '$dir' && $command\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="$title" -- bash -c "cd '$dir' && $command; exec bash"
        elif command -v konsole &> /dev/null; then
            konsole --title "$title" -e bash -c "cd '$dir' && $command; exec bash"
        else
            xterm -title "$title" -e bash -c "cd '$dir' && $command; exec bash" &
        fi
    else
        # Fallback - run in background
        cd "$dir" && $command &
    fi
}

# Start Frontend
echo "Starting Frontend..."
open_terminal "Frontend" "npm run dev" "$SCRIPT_DIR/chat-frontend"

# Start Backend
echo "Starting Backend..."
open_terminal "Backend" "source venv/bin/activate && python server.py" "$SCRIPT_DIR/backend"

# Start MCP Server
echo "Starting MCP Server..."
open_terminal "MCP Server" "source venv/bin/activate && python main.py" "$SCRIPT_DIR/splitwise-mcp"

echo "All services started in separate terminals."
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "MCP:      http://localhost:4200" 