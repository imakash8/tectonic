"""
Core trading engine service
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
from app.utils.validators import ValidationGates
from app.models.trade import Trade, Position, ActivityLog
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class TradingEngine:
    """Core trading bot logic and signal generation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validators = ValidationGates()
        self.MIN_RR_RATIO = 1.5
    
    def calculate_atr_based_stop_loss(self, high: float, low: float, close: float, period: int = 14) -> float:
        """Calculate ATR-based stop loss"""
        # Simplified ATR calculation
        tr = max(high - low, abs(high - close), abs(low - close))
        atr = tr * 0.02  # Simplified: 2% of true range
        
        return close - atr
    
    def calculate_fibonacci_target(self, entry: float, stop_loss: float) -> float:
        """Calculate Fibonacci-based take profit (1.618x extension)"""
        risk = abs(entry - stop_loss)
        target = entry + (risk * 1.618)
        
        return target
    
    def validate_trade_signal(self, market_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate trade signal through all 9 gates"""
        
        all_passed, gates_results = self.validators.validate_all_gates(market_data)
        
        return all_passed, gates_results
    
    def generate_trade_signal(
        self,
        symbol: str,
        direction: str,
        market_data: Dict[str, Any],
        ai_confidence: float = 0.0,
        reasoning: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Generate trade signal with validation"""
        
        # Validate through gates
        valid, gates_results = self.validate_trade_signal(market_data)
        
        if not valid:
            failed_gates = [g for g in gates_results.values() if not g["passed"]]
            logger.warning(f"Trade rejected: {failed_gates[0]['reason']}")
            return None
        
        # Calculate prices
        current_price = market_data.get("current_price", 0)
        stop_loss = self.calculate_atr_based_stop_loss(
            market_data.get("high", current_price),
            market_data.get("low", current_price),
            current_price
        )
        take_profit = self.calculate_fibonacci_target(current_price, stop_loss)
        
        # Calculate R:R ratio
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        if rr_ratio < self.MIN_RR_RATIO:
            logger.warning(f"R:R ratio {rr_ratio:.2f} below minimum {self.MIN_RR_RATIO}")
            return None
        
        return {
            "symbol": symbol,
            "direction": direction,
            "entry_price": current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "rr_ratio": rr_ratio,
            "ai_confidence": ai_confidence,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow(),
            "validation_gates": gates_results
        }
    
    def execute_trade(
        self,
        portfolio_id: int,
        signal: Dict[str, Any],
        quantity: int,
        paper_trading: bool = False
    ) -> Optional[Trade]:
        """Execute approved trade signal"""
        
        try:
            trade = Trade(
                portfolio_id=portfolio_id,
                symbol=signal["symbol"],
                direction=signal["direction"],
                entry_price=signal["entry_price"],
                stop_loss=signal["stop_loss"],
                take_profit=signal["take_profit"],
                quantity=quantity,
                ai_confidence=signal["ai_confidence"],
                entry_reasoning=signal["reasoning"],
                status="OPEN",
                validation_gates_passed=signal["validation_gates"],
                paper_trading="paper" if paper_trading else "real"
            )
            
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            # Log activity
            trade_type = "Paper Trade" if paper_trading else "Trade"
            self._log_activity(trade.id, "EXECUTED", f"{trade_type} executed successfully", signal)
            
            logger.info(f"{trade_type} executed: {signal['symbol']} {signal['direction']} @ {signal['entry_price']}")
            return trade
            
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            self.db.rollback()
            return None
    
    def close_trade(
        self,
        trade_id: int,
        exit_price: float,
        close_reason: str
    ) -> Optional[Trade]:
        """Close an open trade and calculate P/L"""
        
        try:
            trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
            
            if not trade or trade.status == "CLOSED":
                logger.warning(f"Cannot close trade {trade_id}")
                return None
            
            # Calculate P/L
            if trade.direction == "BUY":
                pnl = (exit_price - trade.entry_price) * trade.quantity
                pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
            else:  # SELL
                pnl = (trade.entry_price - exit_price) * trade.quantity
                pnl_percent = ((trade.entry_price - exit_price) / trade.entry_price) * 100
            
            # Update trade
            trade.exit_price = exit_price
            trade.pnl = pnl
            trade.pnl_percent = pnl_percent
            trade.close_reason = close_reason
            trade.closed_at = datetime.utcnow()
            trade.status = "CLOSED"
            
            self.db.commit()
            self.db.refresh(trade)
            
            # Log activity
            self._log_activity(
                trade.id,
                "CLOSED",
                f"Trade closed: P/L {pnl:.2f} ({pnl_percent:.2f}%)",
                {"exit_price": exit_price, "pnl": pnl, "pnl_percent": pnl_percent}
            )
            
            logger.info(f"Trade closed: {trade.symbol} P/L {pnl:.2f}")
            return trade
            
        except Exception as e:
            logger.error(f"Error closing trade: {str(e)}")
            self.db.rollback()
            return None
    
    def _log_activity(self, trade_id: int, event_type: str, reason: str, details: Dict[str, Any]):
        """Log trade activity"""
        try:
            # Convert any datetime objects to strings for JSON serialization
            serializable_details = self._serialize_details(details)
            
            log = ActivityLog(
                trade_id=trade_id,
                event_type=event_type,
                reason=reason,
                details=serializable_details
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
    
    def _serialize_details(self, obj: Any) -> Any:
        """Recursively convert datetime objects to ISO format strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_details(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_details(item) for item in obj]
        else:
            return obj
