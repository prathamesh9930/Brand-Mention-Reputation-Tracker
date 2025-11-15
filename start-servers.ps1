# Brand Tracker - Server Startup Script
Write-Host "🚀 Starting Brand Tracker Servers..." -ForegroundColor Green

# Start Backend Server
Write-Host "📡 Starting Backend API (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\PRATHAMESH\OneDrive\Desktop\My Projects\Under progress projects\something new\backend'; & 'C:/Program Files/Python312/python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# Wait a moment
Start-Sleep -Seconds 3

# Start Frontend Server  
Write-Host "🌐 Starting Frontend App (Port 3001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\PRATHAMESH\OneDrive\Desktop\My Projects\Under progress projects\something new\frontend'; npm run dev"

# Wait a moment
Start-Sleep -Seconds 5

Write-Host "✅ Servers are starting up!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

# Open the app in browser
Write-Host "🌐 Opening Brand Tracker in browser..." -ForegroundColor Magenta
Start-Sleep -Seconds 3
Start-Process "http://localhost:3001"