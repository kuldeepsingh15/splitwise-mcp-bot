# Start all three services in separate windows
Write-Host "Starting all three services..." -ForegroundColor Green

# Get the current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start the frontend (React/Vite)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\chat-frontend'; npm run dev" -WindowStyle Normal

# Start the backend server (FastAPI/Uvicorn)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\mcp-use'; python server.py" -WindowStyle Normal

# Start the MCP server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\splitwise-mcp'; python main.py server" -WindowStyle Normal

Write-Host "All services are starting in separate windows..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "MCP Server will be available at: http://localhost:4200" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this script (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 