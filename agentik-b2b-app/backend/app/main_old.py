from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Import routers
from app.api.routes import rfq, supplier, offer, email, notification, auth
from app.api.routes import orchestrator
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.core.config import settings

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentik B2B API...")
    
    # Initialize connections
    await init_db()
    await init_redis()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agentik B2B API...")

# Create FastAPI app
app = FastAPI(
    title="Agentik B2B Tedarik API",
    description="AI-powered B2B procurement platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(rfq.router, prefix="/api/v1/rfqs", tags=["RFQs"])
app.include_router(supplier.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(offer.router, prefix="/api/v1/offers", tags=["Offers"])
app.include_router(email.router, prefix="/api/v1/emails", tags=["Email"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Agentik B2B API"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Agentik B2B Tedarik API'sine hoş geldiniz!",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )