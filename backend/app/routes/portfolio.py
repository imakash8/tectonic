"""
Portfolio routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Portfolio, User
from app.routes.auth import get_current_user
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

class CreatePortfolioRequest(BaseModel):
    name: str
    starting_capital: float
    description: str = None

@router.post("/")
async def create_portfolio(
    request: CreatePortfolioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new portfolio"""
    try:
        if not request.name or not request.starting_capital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio name and starting capital are required"
            )
        
        if request.starting_capital <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Starting capital must be greater than 0"
            )
        
        # Create new portfolio
        portfolio = Portfolio(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            starting_capital=request.starting_capital,
            current_equity=request.starting_capital,
            cash_balance=request.starting_capital,
            is_active=True
        )
        
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        
        return {
            "id": portfolio.id,
            "user_id": portfolio.user_id,
            "name": portfolio.name,
            "description": portfolio.description,
            "starting_capital": portfolio.starting_capital,
            "current_equity": portfolio.current_equity,
            "cash_balance": portfolio.cash_balance,
            "return_pct": 0,
            "is_active": portfolio.is_active,
            "created_at": portfolio.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating portfolio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portfolio: {str(e)}"
        )

@router.get("/")
async def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's portfolios"""
    try:
        portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).all()
        return [{
            "id": p.id,
            "user_id": p.user_id,
            "name": p.name,
            "starting_capital": p.starting_capital,
            "current_equity": p.current_equity,
            "cash_balance": p.cash_balance,
            "return_pct": ((p.current_equity - p.starting_capital) / p.starting_capital * 100) if p.starting_capital else 0,
            "is_active": p.is_active,
            "created_at": p.created_at
        } for p in portfolios]
    except Exception as e:
        logger.error(f"Error fetching portfolios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{portfolio_id}")
async def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio details"""
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Calculate stats
        total_trades = len(portfolio.trades)
        closed_trades = sum(1 for t in portfolio.trades if t.status == "CLOSED")
        total_pnl = sum(t.pnl for t in portfolio.trades if t.pnl)
        winning_trades = sum(1 for t in portfolio.trades if t.pnl and t.pnl > 0)
        
        return {
            "id": portfolio.id,
            "user_id": portfolio.user_id,
            "name": portfolio.name,
            "description": portfolio.description,
            "starting_capital": portfolio.starting_capital,
            "current_equity": portfolio.current_equity,
            "cash_balance": portfolio.cash_balance,
            "return_pct": ((portfolio.current_equity - portfolio.starting_capital) / portfolio.starting_capital * 100) if portfolio.starting_capital else 0,
            "total_trades": total_trades,
            "closed_trades": closed_trades,
            "open_positions": len(portfolio.positions),
            "total_pnl": total_pnl,
            "win_rate": (winning_trades / closed_trades * 100) if closed_trades > 0 else 0,
            "is_active": portfolio.is_active,
            "created_at": portfolio.created_at,
            "updated_at": portfolio.updated_at
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
