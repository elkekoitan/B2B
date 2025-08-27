from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Import routers
from app.api.routes import rfq, supplier, offer, email, notification, auth
from app.api.routes import orchestrator, rfq_templates
from app.api.routes import catalog, verification, auth_2fa
from app.api.routes import utils
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.core.config import settings
from app.core.middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    starlette_exception_handler,
    BusinessLogicError,
    DatabaseError,
    AuthenticationError,
    AuthorizationError,
    business_logic_exception_handler,
    database_exception_handler,
    authentication_exception_handler,
    authorization_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Agentik B2B API...")
    try:
        await init_db()
        await init_redis()
        logger.info("All connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize connections: {e}")
        raise
    yield
    logger.info("Shutting down Agentik B2B API...")


app = FastAPI(
    title="Agentik B2B Tedarik API",
    description="AI-powered B2B procurement platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.add_middleware(LoggingMiddleware)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
app.add_exception_handler(DatabaseError, database_exception_handler)
app.add_exception_handler(AuthenticationError, authentication_exception_handler)
app.add_exception_handler(AuthorizationError, authorization_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Security
security = HTTPBearer()

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(rfq.router, prefix="/api/v1/rfqs", tags=["RFQs"])
app.include_router(rfq_templates.router, prefix="/api/v1/rfqs/templates", tags=["RFQ Templates"])
app.include_router(supplier.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(offer.router, prefix="/api/v1/offers", tags=["Offers"])
app.include_router(email.router, prefix="/api/v1/emails", tags=["Email"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
app.include_router(catalog.router, prefix="/api/v1/catalog", tags=["Catalog"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Verification"])
app.include_router(auth_2fa.router, prefix="/api/v1/auth/2fa", tags=["Authentication"])
app.include_router(utils.router, prefix="/api/v1/utils", tags=["Utilities"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "Agentik B2B API", "version": "1.0.0"}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    from app.core.database import test_connection
    from app.core.redis_client import redis_client

    health_status = {
        "status": "healthy",
        "service": "Agentik B2B API",
        "version": "1.0.0",
        "checks": {"database": "unknown", "redis": "unknown"},
    }
    try:
        db_healthy = await test_connection()
        health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    try:
        if redis_client:
            await redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    return health_status


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Agentik B2B Tedarik API'sine hoş geldiniz!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "rfqs": "/api/v1/rfqs",
            "rfq_templates": "/api/v1/rfqs/templates",
            "suppliers": "/api/v1/suppliers",
            "offers": "/api/v1/offers",
            "emails": "/api/v1/emails",
            "notifications": "/api/v1/notifications",
            "orchestrator": "/api/v1/orchestrator",
            "catalog": "/api/v1/catalog",
            "verification": "/api/v1/verification",
            "auth_2fa": "/api/v1/auth/2fa",
            "utils": "/api/v1/utils",
        },
    }


@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    return {
        "name": "Agentik B2B API",
        "version": "1.0.0",
        "description": "AI-powered B2B procurement platform API",
        "features": [
            "RFQ Management",
            "Supplier Management",
            "Offer Management",
            "Email Integration",
            "Real-time Notifications",
            "AI Agent Orchestration",
        ],
        "authentication": "Bearer Token (Supabase JWT)",
        "rate_limit": "100 requests per minute",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
