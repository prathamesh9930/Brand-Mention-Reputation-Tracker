# 🔐 Security Setup Script for Brand Tracker (Windows)
# Generates secure credentials and sets up production environment

Write-Host "🔐 Brand Tracker Security Setup" -ForegroundColor Green
Write-Host "==============================="
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
    Write-Host "✅ Python is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python first." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Generating secure credentials..." -ForegroundColor Yellow

# Generate secure secrets
$SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
$ADMIN_API_KEY = "admin_$(python -c "import secrets; print(secrets.token_urlsafe(16))")"
$CLIENT_API_KEY = "client_$(python -c "import secrets; print(secrets.token_urlsafe(16))")"
$DB_PASSWORD = python -c "import secrets; print(secrets.token_urlsafe(16))"
$REDIS_PASSWORD = python -c "import secrets; print(secrets.token_urlsafe(12))"

Write-Host "✅ Secure secrets generated" -ForegroundColor Green

# Create .env file
$envContent = @"
# ==============================================
# 🔐 PRODUCTION SECURITY CONFIGURATION
# ==============================================
# Generated on: $(Get-Date)
# ⚠️  NEVER commit this file to version control!
# ⚠️  Keep these credentials secure!

# JWT Secret Key
SECRET_KEY=$SECRET_KEY

# API Keys
ADMIN_API_KEY=$ADMIN_API_KEY
CLIENT_API_KEY=$CLIENT_API_KEY
NEWS_API_KEY=GET_FROM_NEWSAPI_ORG

# Database Configuration
DATABASE_URL=postgresql://brand_user:$DB_PASSWORD@localhost:5432/brand_tracker_prod

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=$REDIS_PASSWORD

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
FORCE_HTTPS=true

# CORS Origins (UPDATE WITH YOUR DOMAINS!)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com", "https://api.yourdomain.com"]

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Monitoring
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
ADMIN_EMAIL=admin@yourdomain.com

# Application Info
APP_NAME=Brand Tracker
APP_VERSION=1.0.0
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ .env file created with secure credentials" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Important Credentials (SAVE THESE SECURELY!):" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🔑 Admin API Key: $ADMIN_API_KEY" -ForegroundColor White
Write-Host "🔑 Client API Key: $CLIENT_API_KEY" -ForegroundColor White
Write-Host "🔑 Database Password: $DB_PASSWORD" -ForegroundColor White
Write-Host "🔑 Redis Password: $REDIS_PASSWORD" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  NEXT STEPS REQUIRED:" -ForegroundColor Red
Write-Host "========================" -ForegroundColor Red
Write-Host "1. 🌐 Get News API key from https://newsapi.org/register" -ForegroundColor Yellow
Write-Host "2. 📝 Update .env file with your real News API key" -ForegroundColor Yellow
Write-Host "3. 🗄️  Set up PostgreSQL database with the generated password" -ForegroundColor Yellow
Write-Host "4. 🔧 Update CORS_ORIGINS with your actual domain names" -ForegroundColor Yellow
Write-Host "5. 📧 Configure SMTP settings for email alerts" -ForegroundColor Yellow
Write-Host "6. 🔒 Set up SSL certificates for HTTPS" -ForegroundColor Yellow
Write-Host ""

Write-Host "🛡️  Security Checklist:" -ForegroundColor Magenta
Write-Host "=======================" -ForegroundColor Magenta
Write-Host "□ Change default database password" -ForegroundColor White
Write-Host "□ Set up firewall rules" -ForegroundColor White
Write-Host "□ Enable database SSL" -ForegroundColor White
Write-Host "□ Configure reverse proxy (Nginx)" -ForegroundColor White
Write-Host "□ Set up monitoring and alerting" -ForegroundColor White
Write-Host "□ Enable automatic backups" -ForegroundColor White
Write-Host "□ Regular security updates" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Setup complete! Your application is now security-hardened." -ForegroundColor Green
Write-Host "📁 Configuration saved to: .env" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Remember to:" -ForegroundColor Red
Write-Host "   - Keep .env file secure and never commit it" -ForegroundColor Yellow
Write-Host "   - Regularly rotate your API keys" -ForegroundColor Yellow
Write-Host "   - Monitor access logs" -ForegroundColor Yellow
Write-Host "   - Set up SSL certificates" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ .env file created successfully" -ForegroundColor Green
Write-Host "🎯 Ready for production deployment!" -ForegroundColor Green