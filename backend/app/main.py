"""
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db, SessionLocal
from app.routes import trading, market, portfolio, analytics, auth, watchlist, analysis, payments
from app.models import User
import bcrypt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered trading platform with 9-gate validation system",
    version="1.0.0"
)

# Add CORS middleware
logger.info(f"Setting up CORS with allowed origins: {settings.get_allowed_origins()}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Include routers
app.include_router(auth.router)
app.include_router(trading.router)
app.include_router(market.router)
app.include_router(portfolio.router)
app.include_router(analytics.router)
app.include_router(watchlist.router)
app.include_router(analysis.router)
app.include_router(payments.router)

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Tectonic Trading Platform...")
    init_db()
    logger.info("Database initialized")



@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Tectonic Trading Platform...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tectonic Trading Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Tectonic Trading Platform API"
    }

@app.get("/health/db")
async def health_check_db():
    """Database health check endpoint"""
    try:
        db = SessionLocal()
        # Try a simple query to verify database connection
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "database_url_configured": bool(settings.DATABASE_URL and settings.DATABASE_URL != "sqlite:///./tectonic.db")
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
