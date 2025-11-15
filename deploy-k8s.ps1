# Kubernetes Deployment Script for Brand Tracker (Windows)

Write-Host "Deploying Brand Tracker to Kubernetes..." -ForegroundColor Green

# Check if kubectl is available
try {
    kubectl version --client --output=json | Out-Null
    Write-Host "✓ kubectl is available" -ForegroundColor Green
} catch {
    Write-Host "Error: kubectl is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if cluster is accessible
try {
    kubectl cluster-info | Out-Null
    Write-Host "✓ Kubernetes cluster is accessible" -ForegroundColor Green
} catch {
    Write-Host "Error: Cannot connect to Kubernetes cluster" -ForegroundColor Red
    exit 1
}

# Create namespace
Write-Host "Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap and Secrets
Write-Host "Creating ConfigMap and Secrets..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml

# Deploy PostgreSQL
Write-Host "Deploying PostgreSQL..." -ForegroundColor Yellow
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy Redis
Write-Host "Deploying Redis..." -ForegroundColor Yellow
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
Write-Host "Waiting for databases to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=postgres -n brand-tracker --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n brand-tracker --timeout=300s

Write-Host "✓ Databases are ready" -ForegroundColor Green

# Deploy Backend
Write-Host "Deploying Backend..." -ForegroundColor Yellow
kubectl apply -f k8s/backend-deployment.yaml

# Wait for backend to be ready
Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=backend -n brand-tracker --timeout=300s

Write-Host "✓ Backend is ready" -ForegroundColor Green

# Deploy Frontend
Write-Host "Deploying Frontend..." -ForegroundColor Yellow
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for frontend to be ready
Write-Host "Waiting for frontend to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=frontend -n brand-tracker --timeout=300s

Write-Host "✓ Frontend is ready" -ForegroundColor Green

# Deploy Ingress
Write-Host "Deploying Ingress..." -ForegroundColor Yellow
kubectl apply -f k8s/ingress.yaml

Write-Host ""
Write-Host "🚀 Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Services status:" -ForegroundColor Cyan
kubectl get pods -n brand-tracker
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "- Frontend: Update ingress.yaml with your domain" -ForegroundColor White
Write-Host "- Backend API: Update ingress.yaml with your API domain" -ForegroundColor White
Write-Host ""
Write-Host "To check logs:" -ForegroundColor Cyan
Write-Host "  kubectl logs -f deployment/backend -n brand-tracker" -ForegroundColor White
Write-Host "  kubectl logs -f deployment/frontend -n brand-tracker" -ForegroundColor White
Write-Host ""
Write-Host "To scale services:" -ForegroundColor Cyan
Write-Host "  kubectl scale deployment backend --replicas=3 -n brand-tracker" -ForegroundColor White
Write-Host "  kubectl scale deployment frontend --replicas=3 -n brand-tracker" -ForegroundColor White