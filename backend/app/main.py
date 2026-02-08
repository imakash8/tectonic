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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
    
    # Seed test data if no users exist
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("No users found, seeding test data...")
            _seed_test_data(db)
            logger.info("Test data seeded successfully")
    except Exception as e:
        logger.error(f"Error checking/seeding users: {str(e)}")
    finally:
        db.close()

def _seed_test_data(db):
    """Seed test data into database"""
    from app.models import Portfolio, Trade
    from datetime import datetime, timedelta
    
    try:
        # Create test users with simple passwords
        test_users = [
            ("demo@example.com", "demo123", "Demo User"),
            ("trader@example.com", "trader123", "John Trader"),
            ("investor@example.com", "investor123", "Jane Investor"),
        ]
        
        users = []
        for email, password, full_name in test_users:
            # Hash password using bcrypt
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            user = User(
                email=email,
                password_hash=hashed,
                full_name=full_name,
                is_active=True,
                is_premium=(email == "trader@example.com")
            )
            users.append(user)
        
        db.add_all(users)
        db.commit()
        logger.info(f"Created {len(users)} test users")
        
        # Create portfolios for each user
        portfolios = []
        for i, user in enumerate(users):
            portfolio = Portfolio(
                user_id=user.id,
                name=f"Portfolio {i+1}",
                description=f"Test portfolio for {user.full_name}",
                starting_capital=50000.0 + (i * 25000),
                current_equity=52500.0 + (i * 28000),
                cash_balance=15000.0 + (i * 10000),
                is_active=True
            )
            portfolios.append(portfolio)
        
        db.add_all(portfolios)
        db.commit()
        logger.info(f"Created {len(portfolios)} portfolios")
        
        # Create sample trades
        trade_symbols = ["AAPL", "MSFT", "GOOGL"]
        trades_created = 0
        try:
            for portfolio in portfolios:
                for j in range(3):
                    trade = Trade(
                        portfolio_id=portfolio.id,
                        symbol=trade_symbols[j],
                        direction="BUY" if j % 2 == 0 else "SELL",
                        entry_price=150.0 + (j * 50),
                        exit_price=160.0 + (j * 50) if j < 2 else None,
                        quantity=10 + j,
                        stop_loss=140.0,
                        take_profit=170.0,
                        status="CLOSED" if j < 2 else "OPEN",
                        pnl=500.0 if j < 2 else None,
                        pnl_percent=5.0 if j < 2 else None,
                        opened_at=datetime.utcnow() - timedelta(days=30-j*10),
                        closed_at=datetime.utcnow() - timedelta(days=15-j*10) if j < 2 else None,
                    )
                    db.add(trade)
                    trades_created += 1
            
            db.commit()
            logger.info(f"Created {trades_created} trades")
        except Exception as trade_err:
            logger.error(f"Error creating trades: {str(trade_err)}", exc_info=True)
            db.rollback()
            trades_created = 0
        
        logger.info("Test data seeded successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding test data: {str(e)}", exc_info=True)
        raise


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
