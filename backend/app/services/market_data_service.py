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
        Get current quote for symbol from Finnhub or Alpha Vantage
        
        Returns standardized quote data with current_price, high, low, etc.
        Falls back to mock data if no API key is configured
        """
        
        if not settings.USE_REAL_TIME_DATA:
            return self._get_mock_quote(symbol)
        
        try:
            # Check cache first
            if symbol in self.cache:
                cached_data, cache_time = self.cache[symbol]
                if (datetime.utcnow() - cache_time).total_seconds() < self.cache_ttl:
                    logger.debug(f"Returning cached quote for {symbol}")
                    return cached_data
            
            # Try Finnhub first (real-time)
            if self.finnhub_key and self.finnhub_key != "your_finnhub_key_here":
                quote = await self._get_finnhub_quote(symbol)
                if quote:
                    self.cache[symbol] = (quote, datetime.utcnow())
                    return quote
            
            # Fallback to Alpha Vantage (15min delayed)
            if self.alpha_vantage_key and self.alpha_vantage_key != "your_alpha_vantage_key_here":
                quote = await self._get_alpha_vantage_quote(symbol)
                if quote:
                    self.cache[symbol] = (quote, datetime.utcnow())
                    return quote
            
            # If no real API configured, return mock
            logger.warning(f"No real API configured, returning mock data for {symbol}")
            return self._get_mock_quote(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return self._get_mock_quote(symbol)
    
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
        """Get company profile/info from Finnhub API with fallback to mock data"""
        
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
                        
                        logger.info(f"Fetched profile for {symbol}: {profile['name']}")
                        return profile
                    else:
                        logger.warning(f"No profile data from Finnhub for: {symbol}")
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(f"Finnhub rate limit reached for profile")
                else:
                    logger.warning(f"Finnhub API error: {e.response.status_code} for profile")
            except Exception as e:
                logger.warning(f"Error fetching profile from Finnhub for {symbol}: {str(e)}")
        
        # Fall back to mock profile data
        logger.info(f"Returning mock profile data for {symbol}")
        return self._get_mock_profile(symbol)
    
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
    
    def _get_mock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fallback mock data for testing/development
        Returns consistent mock data based on symbol
        """
        
        import random
        
        # Consistent mock prices based on symbol
        symbol_hash = hash(symbol.upper()) % 100
        base_price = 100 + (symbol_hash * 1.5)
        variation = random.uniform(-5, 5)
        current = base_price + variation
        
        return {
            "symbol": symbol.upper(),
            "current_price": round(current, 2),
            "high": round(current + 10, 2),
            "low": round(current - 10, 2),
            "open": round(base_price, 2),
            "prev_close": round(base_price - 2, 2),
            "timestamp": datetime.utcnow(),
            "currency": "USD",
            "source": "mock",
            "note": "Mock data - API key not configured"
        }
    
    def _get_mock_profile(self, symbol: str) -> Dict[str, Any]:
        """
        Mock company profile data for testing/development
        """
        
        # Mock company profiles
        mock_profiles = {
            "AAPL": {
                "name": "Apple Inc.",
                "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
                "logo": "https://logo.clearbit.com/apple.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Consumer Electronics",
                "website": "https://www.apple.com"
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "description": "Microsoft Corporation develops, licenses, and supports software, services and devices worldwide.",
                "logo": "https://logo.clearbit.com/microsoft.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Software",
                "website": "https://www.microsoft.com"
            },
            "TSLA": {
                "name": "Tesla, Inc.",
                "description": "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles.",
                "logo": "https://logo.clearbit.com/tesla.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Automotive",
                "website": "https://www.tesla.com"
            },
            "GOOGL": {
                "name": "Alphabet Inc.",
                "description": "Alphabet Inc. offers various products and platforms in the United States, Europe, and internationally.",
                "logo": "https://logo.clearbit.com/google.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Information Technology",
                "website": "https://www.alphabet.com"
            },
            "AMZN": {
                "name": "Amazon.com, Inc.",
                "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.",
                "logo": "https://logo.clearbit.com/amazon.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Retail",
                "website": "https://www.amazon.com"
            },
            "META": {
                "name": "Meta Platforms, Inc.",
                "description": "Meta Platforms, Inc. engages in the development of products that enable people to connect and share with friends and family through mobile devices.",
                "logo": "https://logo.clearbit.com/meta.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Internet Services",
                "website": "https://www.meta.com"
            },
            "NVDA": {
                "name": "NVIDIA Corporation",
                "description": "NVIDIA Corporation provides graphics, and compute and networking solutions in the United States, Taiwan, China, and internationally.",
                "logo": "https://logo.clearbit.com/nvidia.com",
                "exchange": "NASDAQ",
                "country": "US",
                "industry": "Semiconductors",
                "website": "https://www.nvidia.com"
            },
            "JPM": {
                "name": "JPMorgan Chase & Co.",
                "description": "JPMorgan Chase & Co. operates as a financial services company worldwide.",
                "logo": "https://logo.clearbit.com/jpmorganchase.com",
                "exchange": "NYSE",
                "country": "US",
                "industry": "Financial Services",
                "website": "https://www.jpmorganchase.com"
            }
        }
        
        symbol_upper = symbol.upper()
        
        if symbol_upper in mock_profiles:
            return {
                "symbol": symbol_upper,
                **mock_profiles[symbol_upper]
            }
        
        # Generic mock profile for unknown symbols
        return {
            "symbol": symbol_upper,
            "name": f"{symbol_upper} Corp.",
            "description": f"Public company trading under symbol {symbol_upper}",
            "logo": f"https://logo.clearbit.com/{symbol_upper.lower()}.com",
            "exchange": "NASDAQ",
            "country": "US",
            "industry": "Unknown",
            "website": f"https://www.{symbol_upper.lower()}.com"
        }
    
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