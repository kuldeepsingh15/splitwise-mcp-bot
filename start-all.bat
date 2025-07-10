@echo off
echo Starting all three services...

REM Start the frontend (React/Vite)
start "Frontend - Chat App" powershell -NoExit -Command "cd '%~dp0chat-frontend'; npm run dev"

REM Start the backend server (FastAPI/Uvicorn) with venv
start "Backend - API Server" powershell -NoExit -Command "cd '%~dp0backend'; .\venv\Scripts\Activate.ps1; python server.py"

REM Start the MCP server with venv
start "MCP Server - Splitwise" powershell -NoExit -Command "cd '%~dp0splitwise-mcp'; .\venv\Scripts\Activate.ps1; python main.py server"

echo All services are starting in separate windows...
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend API will be available at: http://localhost:8000
echo MCP Server will be available at: http://localhost:4200
echo.
pause 