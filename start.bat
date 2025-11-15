@echo off
echo 🚀 Starting Brand Mention ^& Reputation Tracker...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

echo ✅ Dependencies found!

REM Start backend
echo 🚀 Starting backend...
cd backend
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo 🚀 Starting frontend...
cd ..\frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo 🎉 Brand Mention ^& Reputation Tracker is now running!
echo.
echo 📊 Dashboard: http://localhost:3000
echo 🔧 API Docs: http://localhost:8000/api/docs
echo 📈 API Health: http://localhost:8000/api/health
echo.
echo 💡 Tips for Demo:
echo    1. Add a sample brand (Nike, Apple, Tesla)
echo    2. Watch real-time sentiment updates
echo    3. Check alerts for mention spikes
echo    4. Explore the dashboard features
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

start http://localhost:3000

echo.
echo Services are running in separate windows.
echo Close those windows to stop the servers.
pause