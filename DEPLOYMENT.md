# Brand Tracker - Production Deployment Guide

## 🚀 Deployment Options

This project supports multiple deployment strategies for production environments:

### 1. Docker Compose (Recommended for Single Server)

**Quick Start:**
```bash
# Production deployment
docker-compose up -d

# Development environment
docker-compose -f docker-compose.dev.yml up -d
```

**Features:**
- ✅ PostgreSQL database with persistent storage
- ✅ Redis for caching and sessions
- ✅ Nginx reverse proxy with SSL support
- ✅ Health checks and auto-restart
- ✅ Production-optimized containers

### 2. Kubernetes (Recommended for Scale)

**Prerequisites:**
- Kubernetes cluster (local or cloud)
- kubectl configured
- Docker images built and pushed to registry

**Deployment:**
```bash
# Linux/MacOS
./deploy-k8s.sh

# Windows PowerShell
./deploy-k8s.ps1

# Manual deployment
kubectl apply -f k8s/
```

**Features:**
- ✅ Horizontal pod autoscaling
- ✅ Load balancing across multiple replicas
- ✅ Rolling updates with zero downtime
- ✅ Persistent storage for database
- ✅ Ingress with SSL termination
- ✅ ConfigMaps and Secrets management

## 📋 Pre-Deployment Checklist

### Environment Configuration
- [ ] Set production database credentials
- [ ] Configure Redis connection
- [ ] Add your News API key
- [ ] Set secure SECRET_KEY
- [ ] Update CORS origins for your domain

### SSL/TLS Setup
- [ ] Obtain SSL certificate
- [ ] Configure domain names in ingress
- [ ] Set up cert-manager (for K8s)
- [ ] Update nginx.conf with your domains

### Monitoring & Logs
- [ ] Configure log aggregation
- [ ] Set up health monitoring
- [ ] Configure alerts for downtime
- [ ] Set up backup strategy

## 🔧 Configuration Files

### Docker Environment Variables
```env
DATABASE_URL=postgresql://brand_user:brand_password@postgres:5432/brand_tracker
REDIS_URL=redis://redis:6379
SECRET_KEY=your-super-secure-secret-key-change-me
NEWS_API_KEY=your_news_api_key_here
ENVIRONMENT=production
```

### Kubernetes Secrets (Base64 encoded)
```bash
# Encode secrets
echo -n "your-secret" | base64

# Apply secrets
kubectl apply -f k8s/configmap.yaml
```

## 🏗️ Build Process

### Building Docker Images
```bash
# Backend
docker build -f backend/Dockerfile -t brand-tracker-backend:latest ./backend

# Frontend
docker build -f frontend/Dockerfile -t brand-tracker-frontend:latest ./frontend

# Development
docker build -f Dockerfile.dev -t brand-tracker-dev:latest .
```

### Pushing to Registry
```bash
# Tag for your registry
docker tag brand-tracker-backend:latest your-registry/brand-tracker-backend:latest
docker tag brand-tracker-frontend:latest your-registry/brand-tracker-frontend:latest

# Push
docker push your-registry/brand-tracker-backend:latest
docker push your-registry/brand-tracker-frontend:latest
```

## 📊 Production Monitoring

### Health Endpoints
- Backend: `http://api.your-domain.com/health`
- Frontend: `http://your-domain.com/`

### Key Metrics to Monitor
- **Response Time**: API endpoint latency
- **Error Rate**: HTTP 5xx errors
- **Database Connections**: PostgreSQL connection pool
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Storage**: Database and Redis storage usage

### Log Locations
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes
kubectl logs -f deployment/backend -n brand-tracker
kubectl logs -f deployment/frontend -n brand-tracker
```

## 🔄 Deployment Workflow

### 1. Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Make changes
# Test locally

# Run tests
npm test
python -m pytest
```

### 2. Staging
```bash
# Build and test production images
docker-compose build
docker-compose up -d

# Run integration tests
# Performance testing
```

### 3. Production
```bash
# Kubernetes rolling update
kubectl set image deployment/backend backend=your-registry/brand-tracker-backend:v1.2.0 -n brand-tracker
kubectl set image deployment/frontend frontend=your-registry/brand-tracker-frontend:v1.2.0 -n brand-tracker

# Docker Compose update
docker-compose pull
docker-compose up -d
```

## 🔒 Security Considerations

### Production Security
- [ ] Enable HTTPS everywhere
- [ ] Set secure headers in nginx
- [ ] Use secrets management
- [ ] Regular security updates
- [ ] Database access restrictions
- [ ] API rate limiting

### Network Security
```yaml
# Example network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: brand-tracker-network-policy
spec:
  # Restrict traffic to necessary services only
```

## 📈 Scaling Recommendations

### Vertical Scaling
- **Small**: 1 CPU, 2GB RAM per service
- **Medium**: 2 CPU, 4GB RAM per service
- **Large**: 4 CPU, 8GB RAM per service

### Horizontal Scaling
```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n brand-tracker

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n brand-tracker
```

### Database Scaling
- Use read replicas for heavy read workloads
- Consider PostgreSQL connection pooling
- Monitor query performance

## 🆘 Troubleshooting

### Common Issues
1. **503 Service Unavailable**: Check backend health endpoint
2. **Database Connection Error**: Verify PostgreSQL credentials
3. **CORS Errors**: Update CORS_ORIGINS environment variable
4. **SSL Certificate Issues**: Check cert-manager logs

### Debug Commands
```bash
# Check pod status
kubectl get pods -n brand-tracker

# View pod logs
kubectl logs pod-name -n brand-tracker

# Exec into pod
kubectl exec -it pod-name -n brand-tracker -- /bin/bash

# Check service endpoints
kubectl get endpoints -n brand-tracker
```

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Test database connectivity
4. Review resource limits
5. Check ingress configuration

Remember to update domain names, API keys, and credentials before deploying to production!