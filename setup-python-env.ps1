# 🐍 Python Environment Setup for Brand Tracker Production

Write-Host "🐍 Brand Tracker - Python Environment Setup" -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta

cd backend

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
    $recreate = Read-Host "Recreate virtual environment? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "🗑️  Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    } else {
        Write-Host "⏭️  Using existing virtual environment" -ForegroundColor Green
        & "venv\Scripts\Activate.ps1"
        Write-Host "📦 Installing/updating dependencies..." -ForegroundColor Yellow
        pip install --upgrade pip
        pip install -r requirements.txt
        cd ..
        exit 0
    }
}

Write-Host "🏗️  Creating new virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (-not $?) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Write-Host "💡 Make sure Python 3.8+ is installed" -ForegroundColor Yellow
    cd ..
    exit 1
}

Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor White
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing production dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if (-not $?) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "💡 Check requirements.txt and internet connection" -ForegroundColor Yellow
    cd ..
    exit 1
}

# Test imports
Write-Host "🧪 Testing critical imports..." -ForegroundColor Yellow

$testScript = @'
import sys
import os

try:
    # Test FastAPI
    import fastapi
    print("✅ FastAPI:", fastapi.__version__)
    
    # Test database
    import sqlalchemy
    print("✅ SQLAlchemy:", sqlalchemy.__version__)
    
    # Test web framework
    import uvicorn
    print("✅ Uvicorn: Available")
    
    # Test API dependencies
    import requests
    import pandas
    import numpy
    print("✅ Data libraries: Available")
    
    # Test security
    import passlib
    import jose
    print("✅ Security libraries: Available")
    
    # Test News API
    import newsapi
    print("✅ NewsAPI: Available")
    
    print("\n🎉 All critical dependencies imported successfully!")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
'@

$testScript | Out-File -FilePath "test_imports.py" -Encoding UTF8
python test_imports.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All dependencies working correctly!" -ForegroundColor Green
    Remove-Item "test_imports.py"
} else {
    Write-Host "❌ Some dependencies failed to import" -ForegroundColor Red
    Remove-Item "test_imports.py"
    cd ..
    exit 1
}

# Create activation script for easy access
$activationScript = @'
@echo off
echo 🐍 Activating Brand Tracker Python Environment...
cd backend
call venv\Scripts\activate.bat
echo ✅ Environment activated! You can now run:
echo    python -m uvicorn app.main:app --reload
echo    python test_news_api.py
echo    python -c "from app.main import app; print('✅ App imported successfully')"
cmd /k
'@

$activationScript | Out-File -FilePath "..\activate-env.bat" -Encoding UTF8

Write-Host ""
Write-Host "✅ Python environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Environment Details:" -ForegroundColor Cyan
Write-Host "   Location: $(Get-Location)\venv" -ForegroundColor White
Write-Host "   Python: $(python --version)" -ForegroundColor White
Write-Host "   Pip: $(pip --version)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Quick Commands:" -ForegroundColor Cyan
Write-Host "   Activate: .\activate-env.bat" -ForegroundColor White
Write-Host "   Start API: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   Test API: python test_news_api.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 The environment is now ready for development and production!" -ForegroundColor Yellow

cd ..