"""
Technical Analysis routes - endpoints for technical indicators
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.market_data_service import MarketDataService
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analysis", tags=["analysis"])
market_service = MarketDataService()

@router.get("/technical/{symbol}")
async def get_technical_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get technical analysis for a symbol
    
    This endpoint analyzes RSI, MACD, and volume
    and provides trading signals based on indicators.
    """
    symbol = symbol.upper()
    
    # For demo, using mock data - in production, fetch from API
    # This would integrate with market data service to get price history
    prices_history = [100, 101, 102, 101.5, 103, 102.5, 104, 103, 105, 104.5, 106, 105.5, 107, 106.5, 108]
    volumes_history = [1000000, 1100000, 900000, 1200000, 1050000, 980000, 1150000, 1050000, 1100000, 950000, 1200000, 1050000, 1000000, 1100000, 1150000]
    
    analysis = await market_service.get_technical_analysis(symbol, prices_history, volumes_history)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform technical analysis"
        )
    
    return analysis

@router.get("/rsi/{symbol}")
async def get_rsi(
    symbol: str,
    period: int = 14,
    current_user: User = Depends(get_current_user)
):
    """Get RSI indicator for a symbol"""
    symbol = symbol.upper()
    
    # Mock data for demo
    prices_history = [100, 101, 102, 101.5, 103, 102.5, 104, 103, 105, 104.5, 106, 105.5, 107, 106.5, 108]
    
    rsi = market_service.calculate_rsi(prices_history, period)
    
    if rsi is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate RSI"
        )
    
    return {
        "symbol": symbol,
        "rsi": rsi,
        "overbought": rsi > 70,
        "oversold": rsi < 30,
        "signal": "SELL" if rsi > 70 else "BUY" if rsi < 30 else "HOLD"
    }

@router.get("/macd/{symbol}")
async def get_macd(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get MACD indicator for a symbol"""
    symbol = symbol.upper()
    
    # Mock data for demo
    prices_history = [100, 101, 102, 101.5, 103, 102.5, 104, 103, 105, 104.5, 106, 105.5, 107, 106.5, 108, 109, 110, 111, 110.5, 112, 113, 114, 113.5, 115, 116, 117, 116.5]
    
    macd = market_service.calculate_macd(prices_history)
    
    if macd is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate MACD"
        )
    
    signal = "BUY" if macd["histogram"] > 0 else "SELL"
    
    return {
        "symbol": symbol,
        **macd,
        "signal": signal,
        "crossover": macd["macd"] > macd["signal"]
    }

@router.get("/volume/{symbol}")
async def get_volume_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get volume analysis for a symbol"""
    symbol = symbol.upper()
    
    # Mock data for demo
    volumes_history = [1000000, 1100000, 900000, 1200000, 1050000, 980000, 1150000, 1050000, 1100000, 950000]
    prices_history = [100, 101, 102, 101.5, 103, 102.5, 104, 103, 105, 104.5]
    
    volume_analysis = market_service.calculate_volume_analysis(volumes_history, prices_history)
    
    if volume_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze volume"
        )
    
    return {
        "symbol": symbol,
        **volume_analysis
    }
