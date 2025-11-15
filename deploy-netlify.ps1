# 🚀 Netlify Deployment Script for Brand Tracker
# RapidQuest Hackathon 2025

Write-Host "🚀 DEPLOYING TO NETLIFY!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

# Check if Netlify CLI is installed
try {
    $netlifyVersion = netlify --version
    Write-Host "✅ Netlify CLI found: $netlifyVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Netlify CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g netlify-cli
    Write-Host "✅ Netlify CLI installed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 DEPLOYMENT STEPS:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ Login to Netlify..." -ForegroundColor Yellow
netlify login

Write-Host ""
Write-Host "2️⃣ Initialize Netlify project..." -ForegroundColor Yellow
netlify init

Write-Host ""
Write-Host "3️⃣ Deploy to Netlify..." -ForegroundColor Yellow
netlify deploy --prod

Write-Host ""
Write-Host "🎯 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Your Brand Tracker is now live at:" -ForegroundColor Cyan
Write-Host "https://your-site-name.netlify.app" -ForegroundColor White
Write-Host ""
Write-Host "🏆 Perfect for RapidQuest submission!" -ForegroundColor Magenta
Write-Host ""
Write-Host "💰 Cost: FREE (No payment info required)" -ForegroundColor Green
Write-Host "⚡ Features: Full-stack, Auto HTTPS, Global CDN" -ForegroundColor Green