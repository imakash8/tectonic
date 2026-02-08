"""
Trade and Position models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    direction = Column(String, nullable=False)  # BUY or SELL
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    opened_at = Column(DateTime, default=datetime.utcnow)
    ai_confidence = Column(Float, default=0.0)
    entry_reasoning = Column(Text, nullable=True)
    validation_gates_passed = Column(JSON, default={})
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="positions")
    
    class Config:
        from_attributes = True

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    direction = Column(String, nullable=False)  # BUY or SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    close_reason = Column(String, nullable=True)
    status = Column(String, default="OPEN")  # OPEN, CLOSED
    ai_confidence = Column(Float, default=0.0)
    entry_reasoning = Column(Text, nullable=True)
    validation_gates_passed = Column(JSON, default={})
    paper_trading = Column(String, default="real")  # "real" or "paper"
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="trades")
    activity_logs = relationship("ActivityLog", back_populates="trade", cascade="all, delete-orphan")
    
    class Config:
        from_attributes = True

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    event_type = Column(String, nullable=False)  # EXECUTED, REJECTED, CLOSED
    reason = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    trade = relationship("Trade", back_populates="activity_logs")
    
    class Config:
        from_attributes = True
