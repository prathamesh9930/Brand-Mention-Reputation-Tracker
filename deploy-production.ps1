# 🚀 Production Deployment Script for Brand Tracker
# This script deploys the Brand Tracker to production environment

Write-Host "🚀 Brand Tracker - Production Deployment" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# Check if production environment file exists
if (-not (Test-Path ".env.production")) {
    Write-Host "❌ .env.production not found! Run setup-security.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Production environment configuration found" -ForegroundColor Green

# Deployment options
Write-Host ""
Write-Host "🎯 Choose deployment method:" -ForegroundColor Cyan
Write-Host "1. Docker Compose (Recommended)" -ForegroundColor White
Write-Host "2. Kubernetes" -ForegroundColor White  
Write-Host "3. Manual deployment" -ForegroundColor White
Write-Host "4. Development mode" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🐳 Deploying with Docker Compose..." -ForegroundColor Yellow
        
        # Copy production env
        Copy-Item ".env.production" "backend\.env" -Force
        Copy-Item ".env.production" "frontend\.env.production" -Force
        
        # Build and deploy
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        
        Write-Host "✅ Docker deployment complete!" -ForegroundColor Green
        Write-Host "🌐 Frontend: http://localhost" -ForegroundColor Cyan
        Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host "☸️ Deploying to Kubernetes..." -ForegroundColor Yellow
        
        # Apply Kubernetes configurations
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        kubectl apply -f k8s/ingress.yaml
        
        Write-Host "✅ Kubernetes deployment complete!" -ForegroundColor Green
        Write-Host "🔍 Check status: kubectl get pods -n brand-tracker" -ForegroundColor Cyan
    }
    
    "3" {
        Write-Host "⚙️ Manual deployment mode..." -ForegroundColor Yellow
        
        # Backend setup
        Write-Host "📦 Setting up backend..." -ForegroundColor White
        cd backend
        
        # Activate virtual environment and install dependencies
        if (Test-Path "venv") {
            & "venv\Scripts\Activate.ps1"
        } else {
            python -m venv venv
            & "venv\Scripts\Activate.ps1"
        }
        
        pip install -r requirements.txt
        
        # Copy production environment
        Copy-Item "..\\.env.production" ".env" -Force
        
        # Start backend
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        
        # Frontend setup
        cd ..\frontend
        Write-Host "🌐 Setting up frontend..." -ForegroundColor White
        
        npm install
        Copy-Item "..\.env.production" ".env.production" -Force
        
        # Build and serve frontend
        npm run build
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run preview"
        
        cd ..
        Write-Host "✅ Manual deployment complete!" -ForegroundColor Green
        Write-Host "🌐 Frontend: http://localhost:4173" -ForegroundColor Cyan
        Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
    }
    
    "4" {
        Write-Host "🔧 Development mode deployment..." -ForegroundColor Yellow
        
        # Use existing start script but with better environment
        .\start-servers.ps1
    }
    
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Brand Tracker is now deployed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure your domain DNS to point to this server" -ForegroundColor White
Write-Host "2. Set up SSL certificates (Let's Encrypt recommended)" -ForegroundColor White
Write-Host "3. Configure firewall rules (ports 80, 443, 8000)" -ForegroundColor White
Write-Host "4. Set up monitoring and backups" -ForegroundColor White
Write-Host ""
Write-Host "📞 Useful Commands:" -ForegroundColor Cyan
Write-Host "- Check API health: curl http://localhost:8000/api/health" -ForegroundColor White
Write-Host "- View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "- Stop services: docker-compose down" -ForegroundColor White