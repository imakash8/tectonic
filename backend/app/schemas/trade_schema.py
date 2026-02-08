"""
Pydantic schemas for trade-related endpoints
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class TradeSignalRequest(BaseModel):
    symbol: str
    direction: str  # BUY or SELL
    
    class Config:
        from_attributes = True

class TradeExecutionRequest(BaseModel):
    portfolio_id: int
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: int
    ai_confidence: float = 0.0
    entry_reasoning: Optional[str] = None
    
    class Config:
        from_attributes = True

class TradeCloseRequest(BaseModel):
    exit_price: float
    close_reason: str
    
    class Config:
        from_attributes = True

class TradeResponse(BaseModel):
    id: int
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float]
    stop_loss: float
    take_profit: float
    quantity: int
    pnl: Optional[float]
    pnl_percent: Optional[float]
    status: str
    opened_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ActivityLogResponse(BaseModel):
    id: int
    event_type: str
    reason: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True
