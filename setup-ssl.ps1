# 🔒 SSL Certificate Setup for Brand Tracker Production

Write-Host "🔒 SSL Certificate Setup for Brand Tracker" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

Write-Host ""
Write-Host "🎯 Choose SSL certificate method:" -ForegroundColor Cyan
Write-Host "1. Let's Encrypt (Free, Automatic)" -ForegroundColor White
Write-Host "2. Self-signed (Development/Testing)" -ForegroundColor White
Write-Host "3. Commercial Certificate (Upload existing)" -ForegroundColor White
Write-Host "4. Skip SSL setup" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🌐 Setting up Let's Encrypt certificate..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📋 Prerequisites:" -ForegroundColor White
        Write-Host "1. Domain pointing to this server" -ForegroundColor Gray
        Write-Host "2. Certbot installed" -ForegroundColor Gray
        Write-Host "3. Nginx installed" -ForegroundColor Gray
        Write-Host ""
        
        $domain = Read-Host "Enter your domain name (e.g., brandtracker.com)"
        
        Write-Host "🔧 Certbot command to run:" -ForegroundColor Cyan
        Write-Host "sudo certbot --nginx -d $domain -d api.$domain" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📝 After running certbot, your nginx configuration will be automatically updated." -ForegroundColor Green
    }
    
    "2" {
        Write-Host "🔧 Creating self-signed certificate..." -ForegroundColor Yellow
        
        # Create certificates directory
        if (-not (Test-Path "ssl")) {
            New-Item -ItemType Directory -Name "ssl"
        }
        
        # Generate self-signed certificate
        $domain = Read-Host "Enter domain name (or use localhost)"
        
        Write-Host "🔑 Generating private key and certificate..." -ForegroundColor White
        
        # OpenSSL commands for Windows (requires OpenSSL installed)
        Write-Host "📋 Commands to run (requires OpenSSL):" -ForegroundColor Cyan
        Write-Host "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/private.key -out ssl/certificate.crt -subj `"/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=$domain`"" -ForegroundColor Yellow
        
        Write-Host ""
        Write-Host "⚠️  Self-signed certificates will show browser warnings" -ForegroundColor Red
        Write-Host "✅ Use only for development/testing" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "📁 Commercial certificate setup..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📋 Place your certificate files in the ssl/ directory:" -ForegroundColor White
        Write-Host "- ssl/certificate.crt (or .pem)" -ForegroundColor Gray
        Write-Host "- ssl/private.key" -ForegroundColor Gray
        Write-Host "- ssl/ca-bundle.crt (if provided)" -ForegroundColor Gray
        
        if (-not (Test-Path "ssl")) {
            New-Item -ItemType Directory -Name "ssl"
            Write-Host "✅ Created ssl/ directory" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "📝 Update nginx-https.conf with correct paths:" -ForegroundColor Cyan
        Write-Host "ssl_certificate /path/to/ssl/certificate.crt;" -ForegroundColor Yellow
        Write-Host "ssl_certificate_key /path/to/ssl/private.key;" -ForegroundColor Yellow
    }
    
    "4" {
        Write-Host "⏭️  Skipping SSL setup..." -ForegroundColor Gray
        Write-Host "⚠️  Remember to configure SSL before production use" -ForegroundColor Yellow
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔧 Nginx Configuration Update:" -ForegroundColor Cyan
Write-Host "1. Copy nginx-https.conf to your nginx sites-available/" -ForegroundColor White
Write-Host "2. Update certificate paths in the configuration" -ForegroundColor White  
Write-Host "3. Create symbolic link to sites-enabled/" -ForegroundColor White
Write-Host "4. Test configuration: nginx -t" -ForegroundColor White
Write-Host "5. Reload nginx: nginx -s reload" -ForegroundColor White
Write-Host ""
Write-Host "✅ SSL setup guidance complete!" -ForegroundColor Green