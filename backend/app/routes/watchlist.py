"""
Watchlist routes - API endpoints for managing watchlists
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.watchlist import Watchlist
from app.models.user import User
from app.routes.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

class WatchlistItem(BaseModel):
    id: int
    symbol: str
    added_at: str
    
    class Config:
        from_attributes = True

class AddToWatchlistRequest(BaseModel):
    symbol: str

@router.get("", response_model=List[WatchlistItem])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all symbols in user's watchlist"""
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    return items

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    request: AddToWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add symbol to watchlist"""
    symbol = request.symbol.upper()
    
    # Check if already in watchlist
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol == symbol
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{symbol} already in watchlist"
        )
    
    watchlist_item = Watchlist(user_id=current_user.id, symbol=symbol)
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    return {"message": f"{symbol} added to watchlist", "item": watchlist_item}

@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove symbol from watchlist"""
    symbol = symbol.upper()
    
    item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol == symbol
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{symbol} not found in watchlist"
        )
    
    db.delete(item)
    db.commit()
    return {"message": f"{symbol} removed from watchlist"}

@router.post("/check/{symbol}")
async def check_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if symbol is in watchlist"""
    symbol = symbol.upper()
    
    item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol == symbol
    ).first()
    
    return {"in_watchlist": item is not None}
