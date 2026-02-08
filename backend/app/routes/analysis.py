"""
Technical Analysis routes - endpoints for technical indicators
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.market_data_service import MarketDataService
from app.routes.auth import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
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
    
    try:
        # Fetch REAL quote data
        quote = await market_service.get_quote(symbol)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to fetch real market data for {symbol}"
            )
        
        analysis = await market_service.get_technical_analysis(symbol, [], [])
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform technical analysis"
            )
        
        return analysis
    except Exception as e:
        logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze {symbol}: {str(e)}"
        )

@router.get("/rsi/{symbol}")
async def get_rsi(
    symbol: str,
    period: int = 14,
    current_user: User = Depends(get_current_user)
):
    """Get RSI indicator for a symbol (requires real market data)"""
    symbol = symbol.upper()
    
    try:
        # Fetch REAL quote data
        quote = await market_service.get_quote(symbol)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to fetch real market data for {symbol}"
            )
        
        # RSI calculation would require historical data
        # For now, return quote data with note
        rsi = market_service.calculate_rsi([], period) if hasattr(market_service, 'calculate_rsi') else None
        
        return {
            "symbol": symbol,
            "current_price": quote.get("current_price"),
            "rsi": rsi or "N/A",
            "note": "Technical indicators require historical price data"
        }
    except Exception as e:
        logger.error(f"Error calculating RSI for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate RSI: {str(e)}"
        )

@router.get("/macd/{symbol}")
async def get_macd(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get MACD indicator for a symbol (requires real market data)"""
    symbol = symbol.upper()
    
    try:
        # Fetch REAL quote data
        quote = await market_service.get_quote(symbol)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to fetch real market data for {symbol}"
            )
        
        macd = market_service.calculate_macd([]) if hasattr(market_service, 'calculate_macd') else None
        
        return {
            "symbol": symbol,
            "current_price": quote.get("current_price"),
            "macd": macd or "N/A",
            "note": "MACD calculation requires historical price data"
        }
    except Exception as e:
        logger.error(f"Error calculating MACD for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate MACD: {str(e)}"
        )

@router.get("/volume/{symbol}")
async def get_volume_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get volume analysis for a symbol (requires real market data)"""
    symbol = symbol.upper()
    
    try:
        # Fetch REAL quote data
        quote = await market_service.get_quote(symbol)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to fetch real market data for {symbol}"
            )
        
        return {
            "symbol": symbol,
            "current_price": quote.get("current_price"),
            "volume": quote.get("volume", "N/A"),
            "note": "Volume analysis requires historical volume data"
        }
    except Exception as e:
        logger.error(f"Error analyzing volume for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze volume: {str(e)}"
        )
