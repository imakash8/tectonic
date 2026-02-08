#!/usr/bin/env python3
"""
Test script to fetch the same stock price 10 times consecutively with 2-second pauses
This will help identify if price fluctuations are real market changes or a system bug
"""

import asyncio
import sys
import time
from pathlib import Path
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Load .env file from backend directory BEFORE importing settings
from dotenv import load_dotenv
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_path)

from app.services.market_data_service import MarketDataService
from app.config import settings


async def test_price_consistency():
    """Fetch the same price 10 times with 2-second pauses"""
    
    print("=" * 80)
    print("PRICE CONSISTENCY TEST")
    print("=" * 80)
    print(f"\n📊 Configuration Check:")
    print(f"  • FINNHUB_API_KEY: {settings.FINNHUB_API_KEY[:10]}... (length: {len(settings.FINNHUB_API_KEY)})")
    print(f"  • ALPHA_VANTAGE_KEY: {settings.ALPHA_VANTAGE_KEY[:10] if settings.ALPHA_VANTAGE_KEY else 'NOT SET'}...")
    print(f"  • Cache TTL: {settings.MARKET_DATA_CACHE_TTL} seconds")
    print(f"  • Current time: {asyncio.get_event_loop().time()}")
    
    # Create service instance
    service = MarketDataService()
    
    # Test with AAPL (Apple)
    symbol = 'AAPL'
    results = []
    
    print(f"\n🔍 Fetching {symbol} price 10 times with 2-second intervals:\n")
    print(f"{'Attempt':<10} {'Price':<15} {'High':<12} {'Low':<12} {'Source':<15} {'Time':<8}")
    print("-" * 80)
    
    for i in range(1, 11):
        try:
            # Fetch quote
            quote = await service.get_quote(symbol)
            
            # Extract data
            current_price = quote.get('current_price')
            high = quote.get('high')
            low = quote.get('low')
            source = quote.get('source', 'unknown')
            
            # Record result
            result = {
                'attempt': i,
                'price': current_price,
                'high': high,
                'low': low,
                'source': source,
                'timestamp': time.time()
            }
            results.append(result)
            
            # Print formatted row
            print(f"{i:<10} ${current_price:<14.2f} ${high:<11.2f} ${low:<11.2f} {source:<15} {i*2}s")
            
            # Wait 2 seconds before next fetch (except on last iteration)
            if i < 10:
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"{i:<10} ❌ ERROR: {str(e)}")
            results.append({
                'attempt': i,
                'error': str(e),
                'timestamp': time.time()
            })
    
    # Analysis
    print("\n" + "=" * 80)
    print("📈 ANALYSIS")
    print("=" * 80)
    
    # Get successful results (exclude errors)
    successful_results = [r for r in results if 'price' in r]
    
    if len(successful_results) == 0:
        print("❌ NO SUCCESSFUL REQUESTS - Cannot analyze")
        return
    
    # Extract prices
    prices = [r['price'] for r in successful_results]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    price_range = max_price - min_price
    price_variance = price_range / avg_price * 100
    
    print(f"\n💰 Price Statistics:")
    print(f"  • Min Price: ${min_price:.2f}")
    print(f"  • Max Price: ${max_price:.2f}")
    print(f"  • Average Price: ${avg_price:.2f}")
    print(f"  • Price Range: ${price_range:.2f}")
    print(f"  • Variance: {price_variance:.4f}% (of average)")
    
    # Check if prices are identical
    unique_prices = len(set(p for p in prices))
    print(f"\n  • Unique Prices: {unique_prices} out of {len(prices)}")
    
    # Analyze caching
    sources = [r.get('source') for r in successful_results]
    unique_sources = set(sources)
    print(f"  • Data Sources Used: {', '.join(unique_sources)}")
    
    # Print consistency verdict
    print(f"\n🎯 VERDICT:")
    if price_variance < 0.01:  # Less than 0.01% variation
        print(f"  ✅ PRICES ARE CONSISTENT (variation: {price_variance:.6f}%)")
        print(f"     → This is EXPECTED behavior - market doesn't change in 20 seconds")
        print(f"     → Cache is working correctly")
    elif price_variance < 1.0:  # Less than 1% variation
        print(f"  ⚠️  MINOR PRICE VARIATION ({price_variance:.4f}%)")
        print(f"     → This is NORMAL for real-time market data")
        print(f"     → Market may have moved slightly")
    else:
        print(f"  ❌ SIGNIFICANT PRICE VARIATION ({price_variance:.4f}%)")
        print(f"     → This is ABNORMAL - suggests a system issue")
        print(f"     → Possible causes:")
        print(f"        1. Different API endpoints being called")
        print(f"        2. Cache not working properly")
        print(f"        3. API returning inconsistent data")
        print(f"        4. Symbol resolution issues")
    
    # Detailed breakdown
    print(f"\n📋 Detailed Results:")
    print(f"{'Attempt':<10} {'Price':<12} {'Cached?':<12} {'Status':<15}")
    print("-" * 50)
    
    for i, result in enumerate(results, 1):
        if 'error' in result:
            print(f"{i:<10} {'ERROR':<12} {'N/A':<12} {result['error']:<15}")
        else:
            # Check if from cache (would appear with same price within TTL)
            is_cached = i > 1 and result['price'] == results[i-2]['price']
            cached_status = "✅ YES" if is_cached else "❌ NO"
            print(f"{i:<10} ${result['price']:<11.2f} {cached_status:<12} OK")
    
    # Cache check
    print(f"\n💾 Cache State:")
    print(f"  • Cache size: {len(service.cache)} entries")
    if symbol in service.cache:
        cached_quote, cache_time = service.cache[symbol]
        print(f"  • {symbol} in cache: YES")
        print(f"  • Cached price: ${cached_quote.get('current_price'):.2f}")
        print(f"  • Cache TTL: {service.cache_ttl} seconds")
    else:
        print(f"  • {symbol} in cache: NO")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


async def test_http_direct():
    """Test API directly with HTTP requests to isolate the issue"""
    print("\n\n" + "=" * 80)
    print("DIRECT FINNHUB API TEST (HTTP Requests)")
    print("=" * 80)
    
    import httpx
    from app.config import settings
    
    api_key = settings.FINNHUB_API_KEY
    symbol = "AAPL"
    
    print(f"\n🔍 Testing Finnhub API directly with {symbol}:\n")
    print(f"{'Attempt':<10} {'Price':<15} {'HTTP Status':<15} {'Time':<8}")
    print("-" * 50)
    
    results = []
    
    for i in range(1, 6):  # Test 5 times directly
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://finnhub.io/api/v1/quote"
                params = {
                    "symbol": symbol,
                    "token": api_key
                }
                
                start = time.time()
                response = await client.get(url, params=params)
                elapsed = time.time() - start
                
                data = response.json()
                price = data.get('c')
                
                print(f"{i:<10} ${price:<14.2f} {response.status_code:<15} {elapsed:.3f}s")
                
                results.append({
                    'price': price,
                    'status': response.status_code,
                    'data': data
                })
                
                if i < 5:
                    await asyncio.sleep(2)
                    
        except Exception as e:
            print(f"{i:<10} ❌ ERROR: {str(e)}")
    
    # Analyze
    print("\n" + "-" * 50)
    if results:
        prices = [r['price'] for r in results]
        unique_prices = len(set(prices))
        print(f"\nDirect API Results:")
        print(f"  • Requests: {len(results)}")
        print(f"  • Unique Prices: {unique_prices}")
        print(f"  • All Same Price: {'✅ YES' if unique_prices == 1 else '❌ NO'}")
        print(f"  • Min: ${min(prices):.2f}, Max: ${max(prices):.2f}")


if __name__ == '__main__':
    print("\n🚀 Starting comprehensive price consistency analysis...\n")
    
    # Run tests
    asyncio.run(test_price_consistency())
    asyncio.run(test_http_direct())
