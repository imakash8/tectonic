"""
Watchlist model - tracks symbols users want to monitor
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="watchlist_items")
    
    # Ensure one symbol per user
    __table_args__ = (UniqueConstraint('user_id', 'symbol', name='uq_user_symbol'),)
    
    class Config:
        from_attributes = True
