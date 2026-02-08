"""
Market data service - handles real-time quotes using Finnhub and Alpha Vantage APIs
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for fetching real-time market data"""
    
    def __init__(self):
        self.finnhub_key = settings.FINNHUB_API_KEY
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_KEY
        self.finnhub_url = "https://finnhub.io/api/v1"
        self.alpha_vantage_url = "https://www.alphavantage.co/query"
        self.cache = {}
        self.cache_ttl = settings.MARKET_DATA_CACHE_TTL
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current quote for symbol from Finnhub (REAL DATA ONLY)
        
        Returns standardized quote data with current_price, high, low, etc.
        Raises exception if API data cannot be retrieved.
        """
        
        # Check cache first
        if symbol in self.cache:
            cached_data, cache_time = self.cache[symbol]
            if (datetime.utcnow() - cache_time).total_seconds() < self.cache_ttl:
                logger.debug(f"Returning cached quote for {symbol}")
                return cached_data
        
        try:
            # Try Finnhub first (real-time, primary source)
            if self.finnhub_key and self.finnhub_key != "your_finnhub_key_here":
                quote = await self._get_finnhub_quote(symbol)
                if quote:
                    self.cache[symbol] = (quote, datetime.utcnow())
                    logger.info(f"Successfully fetched real quote for {symbol} from Finnhub: ${quote['current_price']}")
                    return quote
                else:
                    logger.error(f"Finnhub returned no data for {symbol}")
            
            # Fallback to Alpha Vantage (15min delayed, real data)
            if self.alpha_vantage_key and self.alpha_vantage_key != "your_alpha_vantage_key_here":
                quote = await self._get_alpha_vantage_quote(symbol)
                if quote:
                    self.cache[symbol] = (quote, datetime.utcnow())
                    logger.info(f"Successfully fetched real quote for {symbol} from Alpha Vantage: ${quote['current_price']}")
                    return quote
                else:
                    logger.error(f"Alpha Vantage returned no data for {symbol}")
            
            # If we reach here, no real API data available
            logger.error(f"CRITICAL: Unable to fetch real market data for {symbol} - all APIs failed or not configured")
            raise Exception(f"Unable to fetch real market data for {symbol}. Please ensure FINNHUB_API_KEY or ALPHA_VANTAGE_KEY is properly configured.")
                
        except Exception as e:
            logger.error(f"CRITICAL ERROR fetching quote for {symbol}: {str(e)}")
            raise Exception(f"Market data unavailable for {symbol}: {str(e)}")
    
    async def _get_finnhub_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch quote from Finnhub API (real-time)"""
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{self.finnhub_url}/quote"
                params = {
                    "symbol": symbol.upper(),
                    "token": self.finnhub_key
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Check for API errors
                if not data.get('c'):  # No current price
                    logger.warning(f"Invalid symbol or no data from Finnhub: {symbol}")
                    return None
                
                # Format response - use current time since Finnhub quote is real-time
                quote = {
                    "symbol": symbol.upper(),
                    "current_price": data.get('c', 0),
                    "high": data.get('h', data.get('c', 0)),
                    "low": data.get('l', data.get('c', 0)),
                    "open": data.get('o', data.get('c', 0)),
                    "prev_close": data.get('pc', data.get('c', 0)),
                    "timestamp": datetime.utcnow(),  # Real-time data, use current UTC time
                    "currency": "USD",
                    "source": "finnhub"
                }
                
                logger.info(f"Finnhub quote for {symbol}: ${quote['current_price']}")
                return quote
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Finnhub rate limit reached")
            else:
                logger.warning(f"Finnhub API error: {e.response.status_code}")
        except Exception as e:
            logger.warning(f"Finnhub error: {str(e)}")
        
        return None
    
    async def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch quote from Alpha Vantage API (15min delayed)"""
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol.upper(),
                    "apikey": self.alpha_vantage_key
                }
                
                response = await client.get(self.alpha_vantage_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "Global Quote" in data and data["Global Quote"]:
                    quote_data = data["Global Quote"]
                    
                    if not quote_data.get("05. price"):
                        logger.warning(f"Invalid symbol or no data from Alpha Vantage: {symbol}")
                        return None
                    
                    current = float(quote_data.get("05. price", 0))
                    prev_close = float(quote_data.get("08. previous close", current))
                    
                    quote = {
                        "symbol": symbol.upper(),
                        "current_price": current,
                        "high": float(quote_data.get("03. high", current)),
                        "low": float(quote_data.get("04. low", current)),
                        "open": float(quote_data.get("02. open", current)),
                        "prev_close": prev_close,
                        "timestamp": datetime.utcnow(),
                        "currency": "USD",
                        "source": "alpha_vantage",
                        "note": "Data is 15 minutes delayed"
                    }
                    
                    logger.info(f"Alpha Vantage quote for {symbol}: ${quote['current_price']}")
                    return quote
                
        except Exception as e:
            logger.warning(f"Alpha Vantage error: {str(e)}")
        
        return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile/info from Finnhub API (REAL DATA ONLY)"""
        
        # Try Finnhub first if API key is configured
        if self.finnhub_key and self.finnhub_key != "your_finnhub_key_here":
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    url = f"{self.finnhub_url}/stock/profile2"
                    params = {
                        "symbol": symbol.upper(),
                        "token": self.finnhub_key
                    }
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Check if we got valid profile data
                    if data and "name" in data and data.get("name"):
                        profile = {
                            "symbol": symbol.upper(),
                            "name": data.get("name", "Unknown"),
                            "description": data.get("description", ""),
                            "logo": data.get("logo", ""),
                            "exchange": data.get("exchange", ""),
                            "country": data.get("country", ""),
                            "industry": data.get("finnhubIndustry", ""),
                            "website": data.get("weburl", "")
                        }
                        
                        logger.info(f"Fetched real profile for {symbol}: {profile['name']}")
                        return profile
                    else:
                        logger.error(f"Finnhub returned no profile data for: {symbol}")
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.error(f"Finnhub rate limit reached for profile of {symbol}")
                else:
                    logger.error(f"Finnhub API error {e.response.status_code} for profile of {symbol}")
            except Exception as e:
                logger.error(f"Error fetching profile from Finnhub for {symbol}: {str(e)}")
        
        # If we reach here, real API data is unavailable
        logger.error(f"CRITICAL: Unable to fetch real company profile for {symbol} - Finnhub API not configured or failed")
        raise Exception(f"Unable to fetch company profile for {symbol}. Please ensure FINNHUB_API_KEY is properly configured.")
    
    async def get_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent news for symbol from Finnhub"""
        
        if not self.finnhub_key or self.finnhub_key == "your_finnhub_key_here":
            logger.warning("Finnhub API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{self.finnhub_url}/company-news"
                params = {
                    "symbol": symbol.upper(),
                    "limit": min(limit, 20),
                    "token": self.finnhub_key
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                news = response.json()
                
                logger.info(f"Fetched {len(news)} news items for {symbol}")
                return news
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    async def get_crypto_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cryptocurrency price (placeholder)"""
        return None
    
    def clear_cache(self, symbol: Optional[str] = None):
        """Clear the quote cache"""
        if symbol:
            if symbol in self.cache:
                del self.cache[symbol]
            logger.info(f"Cleared cache for {symbol}")
        else:
            self.cache.clear()
            logger.info("Market data cache cleared")

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get market indices overview (SPY, QQQ, IWM, DXY, VIX)"""
        try:
            indices = {}
            symbols = ['SPY', 'QQQ', 'IWM', 'DXY', 'VIX']
            
            for symbol in symbols:
                quote = await self.get_quote(symbol)
                if quote:
                    indices[symbol] = {
                        'price': quote.get('current_price'),
                        'change': quote.get('current_price', 0) - quote.get('prev_close', 0),
                        'change_pct': ((quote.get('current_price', 0) - quote.get('prev_close', 1)) / quote.get('prev_close', 1) * 100) if quote.get('prev_close') else 0
                    }
            
            return indices
        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            return {}

# Create singleton instance
market_data_service = MarketDataService()