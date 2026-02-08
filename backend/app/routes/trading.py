"""
Trading routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TradeResponse, TradeExecutionRequest, TradeCloseRequest
from app.services.trading_engine import TradingEngine
from app.services.market_data_service import market_data_service
from app.models import Trade, Portfolio, User
from app.routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trading", tags=["trading"])

@router.post("/execute")
async def execute_trade(
    request: TradeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a new trade with real market data from Finnhub"""
    try:
        logger.info(f"Trade execution request for {request.symbol} by user {current_user.id}")
        
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == request.portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Check cash balance
        trade_cost = request.entry_price * request.quantity
        if trade_cost > portfolio.cash_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds. Required: ${trade_cost:.2f}, Available: ${portfolio.cash_balance:.2f}"
            )
        
        engine = TradingEngine(db)
        
        # Fetch real market data from Finnhub API (MUST succeed)
        try:
            live_quote = await market_data_service.get_quote(request.symbol)
            logger.info(f"Fetched real quote for {request.symbol}: ${live_quote.get('current_price')} (source: {live_quote.get('source')})")
        except Exception as quote_error:
            logger.error(f"CRITICAL: Failed to fetch real market data for {request.symbol}: {str(quote_error)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to fetch real market data for {request.symbol}. Please ensure API keys are configured and markets are open. Error: {str(quote_error)}"
            )
        
        # Use real market data for validation (NO hardcoded fallbacks)
        from datetime import datetime
        market_data = {
            "current_price": live_quote.get("current_price"),
            "high": live_quote.get("high"),
            "low": live_quote.get("low"),
            "prev_close": live_quote.get("prev_close"),
            "volume": live_quote.get("volume"),
            "volatility": live_quote.get("volatility", 0.2),
            "vix": 20,  # Market volatility proxy
            "market_open": True,
            "entry_price": request.entry_price,
            "stop_loss": request.stop_loss,
            "take_profit": request.take_profit,
            "direction": request.direction,
            "ai_confidence": request.ai_confidence,
            "quote_timestamp": live_quote.get("timestamp") or datetime.utcnow(),
            "quote_source": live_quote.get("source"),
            "timeframe": "day"
        }
        
        # Generate signal
        signal = engine.generate_trade_signal(
            request.symbol,
            request.direction,
            market_data,
            request.ai_confidence,
            request.entry_reasoning or ""
        )
        
        if not signal:
            # Get validation details for better error message
            valid, gates_results = engine.validate_trade_signal(market_data)
            failed_gates = [g for g in gates_results.values() if not g["passed"]]
            failed_reasons = "; ".join([f"Gate {g['gate']}: {g['reason']}" for g in failed_gates])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trade validation failed - {failed_reasons}"
            )
        
        # Execute trade
        trade = engine.execute_trade(request.portfolio_id, signal, request.quantity)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to execute trade"
            )
        
        # Build response with validation gates status
        response = TradeResponse.from_orm(trade)
        response_dict = response.dict()
        response_dict['validation_gates'] = signal.get('validation_gates', {})
        
        return response_dict
        
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/paper/execute")
async def execute_paper_trade(
    request: TradeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a paper trading trade (risk-free practice mode with real market data)"""
    try:
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == request.portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        engine = TradingEngine(db)
        
        # Fetch real market data from Finnhub API
        live_quote = await market_data_service.get_quote(request.symbol)
        
        if not live_quote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to fetch market data for {request.symbol}"
            )
        
        # Use real market data for validation
        from datetime import datetime
        market_data = {
            "current_price": live_quote.get("current_price", request.entry_price),
            "high": live_quote.get("high", request.entry_price * 1.02),
            "low": live_quote.get("low", request.entry_price * 0.98),
            "prev_close": live_quote.get("prev_close", request.entry_price),
            "volume": live_quote.get("volume", 5000000),
            "volatility": live_quote.get("volatility", 0.2),
            "vix": 20,
            "market_open": True,
            "entry_price": request.entry_price,
            "stop_loss": request.stop_loss,
            "take_profit": request.take_profit,
            "direction": request.direction,
            "ai_confidence": request.ai_confidence,
            "quote_timestamp": live_quote.get("timestamp") or datetime.utcnow(),
            "quote_source": live_quote.get("source", "unknown"),
            "timeframe": "day"
        }
        
        signal = engine.generate_trade_signal(
            request.symbol,
            request.direction,
            market_data,
            request.ai_confidence,
            request.entry_reasoning or ""
        )
        
        if not signal:
            # Get validation details for better error message
            valid, gates_results = engine.validate_trade_signal(market_data)
            failed_gates = [g for g in gates_results.values() if not g["passed"]]
            failed_reasons = "; ".join([f"Gate {g['gate']}: {g['reason']}" for g in failed_gates])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trade validation failed - {failed_reasons}"
            )
        
        trade = engine.execute_trade(request.portfolio_id, signal, request.quantity, paper_trading=True)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to execute paper trade"
            )
        
        return TradeResponse.from_orm(trade)
        
    except Exception as e:
        logger.error(f"Error executing paper trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/close/{trade_id}")
async def close_trade(
    trade_id: int,
    request: TradeCloseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close an open trade"""
    try:
        # Verify trade ownership
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        portfolio = db.query(Portfolio).filter(Portfolio.id == trade.portfolio_id).first()
        if not portfolio or portfolio.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to close this trade"
            )
        
        engine = TradingEngine(db)
        trade = engine.close_trade(trade_id, request.exit_price, request.close_reason)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found or already closed"
            )
        
        return TradeResponse.from_orm(trade)
        
    except Exception as e:
        logger.error(f"Error closing trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/trades")
async def get_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trades for current user"""
    try:
        trades = db.query(Trade).join(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).all()
        return [TradeResponse.from_orm(t) for t in trades]
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/trades/{trade_id}")
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific trade"""
    try:
        trade = db.query(Trade).join(Portfolio).filter(
            Trade.id == trade_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        return TradeResponse.from_orm(trade)
        
    except Exception as e:
        logger.error(f"Error fetching trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
