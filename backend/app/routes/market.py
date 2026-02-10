"""
Market data routes
"""

from fastapi import APIRouter, HTTPException, status
from app.services.market_data_service import MarketDataService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/market", tags=["market"])

market_service = MarketDataService()

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get current quote for a symbol"""
    try:
        quote = await market_service.get_quote(symbol.upper())
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote not found for {symbol}"
            )
        
        return quote
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error fetching quote for {symbol}: {error_msg}")
        
        # Provide helpful error message
        if "FINNHUB_API_KEY" in error_msg or "not configured" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Market data service unavailable. API key not configured. Please contact support. Error: {error_msg}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch market data for {symbol}. {error_msg}"
        )

@router.get("/profile/{symbol}")
async def get_company_profile(symbol: str):
    """Get company profile/info for a symbol"""
    try:
        profile = await market_service.get_company_profile(symbol.upper())
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company profile not found for {symbol}"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error fetching company profile for {symbol}: {error_msg}")
        
        # Provide helpful error message
        if "FINNHUB_API_KEY" in error_msg or "not configured" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Market data service unavailable. API key not configured. Please contact support. Error: {error_msg}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch company profile for {symbol}. {error_msg}"
        )

@router.get("/overview")
async def get_market_overview():
    """Get market indices overview"""
    try:
        overview = await market_service.get_market_overview()
        return {
            "indices": overview,
            "status": "Market open" if overview else "Data unavailable"
        }
    except Exception as e:
        logger.error(f"Error fetching market overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/crypto/{symbol}")
async def get_crypto_price(symbol: str):
    """Get cryptocurrency price"""
    try:
        price = await market_service.get_crypto_price(symbol.upper())
        
        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cryptocurrency {symbol} not found"
            )
        
        return price
        
    except Exception as e:
        logger.error(f"Error fetching crypto price: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/search/{query}")
async def search_symbols(query: str):
    """Search for symbols by company name or symbol"""
    try:
        results = await market_service.search_symbols(query)
        
        if not results:
            return {
                "query": query,
                "results": [],
                "message": f"No symbols found for '{query}'"
            }
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching symbols: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
