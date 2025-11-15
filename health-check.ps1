# 📊 Health Check and Monitoring Script for Brand Tracker

Write-Host "📊 Brand Tracker - Health Check & Monitoring" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta

# Check if services are running
Write-Host ""
Write-Host "🔍 Checking service status..." -ForegroundColor Cyan

# Backend health check
Write-Host "🐍 Backend API Status:" -ForegroundColor Yellow
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "✅ Backend API: HEALTHY" -ForegroundColor Green
    Write-Host "   Status: $($backendHealth.status)" -ForegroundColor White
    Write-Host "   Uptime: $($backendHealth.uptime)" -ForegroundColor White
} catch {
    Write-Host "❌ Backend API: OFFLINE" -ForegroundColor Red
}

# Database check
Write-Host ""
Write-Host "🗄️  Database Status:" -ForegroundColor Yellow
if (Test-Path "backend/brand_tracker.db") {
    $dbSize = (Get-Item "backend/brand_tracker.db").Length / 1KB
    Write-Host "✅ Database: ACCESSIBLE" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($dbSize, 2)) KB" -ForegroundColor White
} else {
    Write-Host "❌ Database: NOT FOUND" -ForegroundColor Red
}

# Frontend check
Write-Host ""
Write-Host "🌐 Frontend Status:" -ForegroundColor Yellow
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($frontendTest.StatusCode -eq 200) {
        Write-Host "✅ Frontend: HEALTHY" -ForegroundColor Green
    }
} catch {
    # Try alternative ports
    $altPorts = @(3001, 4173, 5173)
    $frontendFound = $false
    
    foreach ($port in $altPorts) {
        try {
            $test = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2 -UseBasicParsing
            if ($test.StatusCode -eq 200) {
                Write-Host "✅ Frontend: HEALTHY (Port $port)" -ForegroundColor Green
                $frontendFound = $true
                break
            }
        } catch {
            # Continue to next port
        }
    }
    
    if (-not $frontendFound) {
        Write-Host "❌ Frontend: OFFLINE" -ForegroundColor Red
    }
}

# Check News API integration
Write-Host ""
Write-Host "📰 News API Integration:" -ForegroundColor Yellow
if (Test-Path "backend/.env") {
    $envContent = Get-Content "backend/.env" | Where-Object { $_ -match "NEWS_API_KEY" }
    if ($envContent -match "771f41596a4d4d2ab79a6581c9c01024") {
        Write-Host "✅ News API: CONFIGURED (Real key active)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ News API: Key found but may be placeholder" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ News API: Configuration not found" -ForegroundColor Red
}

# Security audit
Write-Host ""
Write-Host "🛡️  Security Status:" -ForegroundColor Yellow

$securityChecks = @{
    "JWT Authentication" = (Test-Path "backend/app/core/security.py")
    "API Key Validation" = (Get-Content "backend/app/core/security.py" -Raw) -match "API_KEY_HEADER"
    "CORS Configuration" = (Get-Content "backend/app/main.py" -Raw) -match "CORSMiddleware"
    "Rate Limiting" = (Get-Content "backend/app/core/security.py" -Raw) -match "rate_limit"
    "HTTPS Configuration" = (Test-Path "nginx-https.conf")
    "Production Secrets" = (Test-Path ".env.production")
}

foreach ($check in $securityChecks.GetEnumerator()) {
    if ($check.Value) {
        Write-Host "   ✅ $($check.Key): ENABLED" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ $($check.Key): NEEDS ATTENTION" -ForegroundColor Yellow
    }
}

# Performance metrics
Write-Host ""
Write-Host "📈 Performance Metrics:" -ForegroundColor Yellow

# Check file counts
$totalFiles = (Get-ChildItem -Recurse -File | Measure-Object).Count
$pyFiles = (Get-ChildItem -Recurse -Filter "*.py" | Measure-Object).Count
$tsFiles = (Get-ChildItem -Recurse -Filter "*.ts*" -Include "*.ts","*.tsx" | Measure-Object).Count

Write-Host "   📁 Total files: $totalFiles" -ForegroundColor White
Write-Host "   🐍 Python files: $pyFiles" -ForegroundColor White
Write-Host "   📜 TypeScript files: $tsFiles" -ForegroundColor White

# Check Docker status
Write-Host ""
Write-Host "🐳 Docker Status:" -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker: AVAILABLE" -ForegroundColor Green
    Write-Host "   Version: $dockerVersion" -ForegroundColor White
    
    # Check if containers are running
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
    if ($containers) {
        Write-Host "   Running containers:" -ForegroundColor White
        $containers | ForEach-Object { Write-Host "   $($_)" -ForegroundColor Gray }
    }
} catch {
    Write-Host "   ⚠️ Docker: NOT AVAILABLE" -ForegroundColor Yellow
}

# Deployment readiness score
Write-Host ""
Write-Host "🏆 Deployment Readiness Score:" -ForegroundColor Cyan

$score = 0
$maxScore = 10

# Calculate score based on checks
if ((Test-Path "backend/app/main.py")) { $score++ }                    # Backend exists
if ((Test-Path "frontend/package.json")) { $score++ }                 # Frontend exists  
if ((Test-Path "backend/brand_tracker.db")) { $score++ }             # Database exists
if ((Test-Path ".env.production")) { $score++ }                       # Production config
if ((Test-Path "docker-compose.yml")) { $score++ }                   # Docker support
if ((Test-Path "k8s")) { $score++ }                                  # Kubernetes support
if ((Test-Path "nginx-https.conf")) { $score++ }                    # HTTPS config
if ((Get-Content "backend/.env" -Raw) -match "771f41596a4d4d2ab79a6581c9c01024") { $score++ } # Real API key
if ((Test-Path "SECURITY.md")) { $score++ }                          # Documentation
if ((Test-Path "deploy-production.ps1")) { $score++ }                # Deployment script

$percentage = ($score / $maxScore) * 100

if ($percentage -eq 100) {
    Write-Host "🎉 PERFECT: $percentage% ($score/$maxScore)" -ForegroundColor Green
    Write-Host "   🚀 Ready for immediate production deployment!" -ForegroundColor Green
} elseif ($percentage -ge 90) {
    Write-Host "🌟 EXCELLENT: $percentage% ($score/$maxScore)" -ForegroundColor Green  
    Write-Host "   ✅ Production ready with minor optimizations" -ForegroundColor Green
} elseif ($percentage -ge 80) {
    Write-Host "👍 GOOD: $percentage% ($score/$maxScore)" -ForegroundColor Yellow
    Write-Host "   🔧 Needs some configuration for production" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ NEEDS WORK: $percentage% ($score/$maxScore)" -ForegroundColor Red
    Write-Host "   🔨 Requires development before deployment" -ForegroundColor Red
}

Write-Host ""
Write-Host "📞 Quick Actions:" -ForegroundColor Cyan
Write-Host "- Start services: .\start-servers.ps1" -ForegroundColor White
Write-Host "- Deploy production: .\deploy-production.ps1" -ForegroundColor White
Write-Host "- Setup SSL: .\setup-ssl.ps1" -ForegroundColor White
Write-Host "- Test News API: python backend/test_news_api.py" -ForegroundColor White