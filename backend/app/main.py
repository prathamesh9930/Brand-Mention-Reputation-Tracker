from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .api.brands import router as brands_router
from .api.mentions import router as mentions_router
from .api.sentiment import router as sentiment_router
from .api.alerts import router as alerts_router
from .api.auth import router as auth_router
from .api.test_endpoints import router as test_router
from .services.mention_collector import MentionCollector
from .services.sentiment_analyzer_simple import SentimentAnalyzer
from .services.alert_system import AlertSystem
from .models.database import init_db
from .core.security import (
    SECURITY_HEADERS, 
    check_rate_limit, 
    verify_api_key,
    verify_jwt_token
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]'))

# Initialize FastAPI app
app = FastAPI(
    title="Brand Mention & Reputation Tracker API",
    description="Secure, real-time brand monitoring with AI-powered sentiment analysis",
    version="1.0.0",
    docs_url="/api/docs" if DEBUG else None,  # Hide docs in production
    redoc_url="/api/redoc" if DEBUG else None,  # Hide redoc in production
    openapi_url="/api/openapi.json" if DEBUG else None  # Hide OpenAPI in production
)

# Security middleware
if FORCE_HTTPS and ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts middleware for production
if ENVIRONMENT == "production":
    allowed_hosts = [host.replace("https://", "").replace("http://", "") for host in CORS_ORIGINS]
    allowed_hosts.extend(["localhost", "127.0.0.1"])  # Allow local access
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS middleware with environment-specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Skip rate limiting for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
    else:
        # Rate limiting check
        client_ip = getattr(request.client, 'host', '127.0.0.1') if request.client else '127.0.0.1'
        if not check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": "3600"}
            )
        
        response = await call_next(request)
    
    # Add security headers
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

# Include routers with authentication
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(test_router, prefix="/api/test", tags=["testing"])
app.include_router(brands_router, prefix="/api/brands", tags=["brands"])
app.include_router(mentions_router, prefix="/api/mentions", tags=["mentions"])
app.include_router(sentiment_router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])

# Global services
mention_collector = MentionCollector()
sentiment_analyzer = SentimentAnalyzer()
alert_system = AlertSystem()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.monitoring_brands: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, brand_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if brand_id:
            if brand_id not in self.monitoring_brands:
                self.monitoring_brands[brand_id] = []
            self.monitoring_brands[brand_id].append(websocket)
        
        logger.info(f"WebSocket connected. Brand ID: {brand_id}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from brand-specific monitoring
        for brand_id, connections in self.monitoring_brands.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: Dict[Any, Any]):
        if self.active_connections:
            message_str = json.dumps(message, default=str)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

    async def send_to_brand_monitors(self, brand_id: str, message: Dict[Any, Any]):
        if brand_id in self.monitoring_brands:
            message_str = json.dumps(message, default=str)
            disconnected = []
            
            for connection in self.monitoring_brands[brand_id]:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Brand Mention & Reputation Tracker API...")
    
    # Initialize database
    await init_db()
    
    # Start background monitoring tasks
    asyncio.create_task(background_mention_collection())
    asyncio.create_task(background_sentiment_analysis())
    asyncio.create_task(background_alert_monitoring())
    
    logger.info("API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Brand Mention & Reputation Tracker API is running!",
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

@app.get("/api/health/detailed")
async def detailed_health_check(api_key_valid: bool = Depends(verify_api_key)):
    """Detailed health check - requires API key"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "environment": ENVIRONMENT,
        "services": {
            "mention_collector": "active",
            "sentiment_analyzer": "active",
            "alert_system": "active",
            "websocket_connections": len(manager.active_connections),
            "database": "connected",
            "security": "enabled"
        },
        "security": {
            "https_enabled": FORCE_HTTPS,
            "rate_limiting": "enabled",
            "authentication": "enabled"
        }
    }

@app.websocket("/ws/mentions")
async def websocket_mentions_endpoint(websocket: WebSocket, brand_id: Optional[str] = None):
    """WebSocket endpoint for real-time mention updates"""
    await manager.connect(websocket, brand_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "subscribe_brand":
                brand_id = message.get("brand_id")
                if brand_id:
                    if brand_id not in manager.monitoring_brands:
                        manager.monitoring_brands[brand_id] = []
                    if websocket not in manager.monitoring_brands[brand_id]:
                        manager.monitoring_brands[brand_id].append(websocket)
                    
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "brand_id": brand_id,
                        "message": f"Subscribed to brand {brand_id} updates"
                    }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

async def background_mention_collection():
    """Background task to collect mentions"""
    while True:
        try:
            logger.info("Running mention collection cycle...")
            
            # Collect mentions for all active brands
            new_mentions = await mention_collector.collect_all_mentions()
            
            # Broadcast new mentions via WebSocket
            for mention in new_mentions:
                await manager.send_to_brand_monitors(
                    mention["brand_id"],
                    {
                        "type": "new_mention",
                        "data": mention
                    }
                )
            
            # Wait before next collection cycle
            await asyncio.sleep(30)  # Collect every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in mention collection: {e}")
            await asyncio.sleep(60)  # Wait longer on error

async def background_sentiment_analysis():
    """Background task to analyze sentiment of new mentions"""
    while True:
        try:
            # Process pending sentiment analysis
            updated_mentions = await sentiment_analyzer.process_pending_mentions()
            
            # Broadcast sentiment updates
            for mention in updated_mentions:
                await manager.send_to_brand_monitors(
                    mention["brand_id"],
                    {
                        "type": "sentiment_update",
                        "data": mention
                    }
                )
            
            await asyncio.sleep(10)  # Analyze every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            await asyncio.sleep(30)

async def background_alert_monitoring():
    """Background task to monitor for alerts and spikes"""
    while True:
        try:
            # Check for mention spikes and sentiment alerts
            new_alerts = await alert_system.check_for_alerts()
            
            # Broadcast alerts
            for alert in new_alerts:
                await manager.broadcast({
                    "type": "alert",
                    "data": alert
                })
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in alert monitoring: {e}")
            await asyncio.sleep(120)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)