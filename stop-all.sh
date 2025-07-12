#!/bin/bash

echo "Stopping all running processes..."

# Kill processes running on specific ports
echo "Stopping processes on ports 8000, 5173, 4200..."

# Kill backend server (port 8000)
pkill -f "python.*server.py" 2>/dev/null || echo "No backend server found"

# Kill frontend dev server (port 5173 or similar)
pkill -f "vite" 2>/dev/null || echo "No frontend server found"

# Kill MCP server (port 4200)
pkill -f "python.*main.py" 2>/dev/null || echo "No MCP server found"

# Kill any node processes related to the project
pkill -f "npm.*dev" 2>/dev/null || echo "No npm dev processes found"

# Kill any processes using the specific ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No processes on port 8000"
lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "No processes on port 5173"
lsof -ti:4200 | xargs kill -9 2>/dev/null || echo "No processes on port 4200"

echo "All processes stopped!"
echo "You can now restart with: npm run dev" 