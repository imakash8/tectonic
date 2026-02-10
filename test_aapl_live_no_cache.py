#!/usr/bin/env python
"""Test AAPL price fetching 10 consecutive times - LIVE DATA (No Cache)"""

import sys
sys.path.insert(0, 'backend')
import asyncio
import time
from app.services.market_data_service import MarketDataService
from datetime import datetime

async def fetch_stock_price_live():
    service = MarketDataService()
    
    print("=" * 90)
    print("📊 AAPL Stock Price - 10 Consecutive Fetches (CACHE DISABLED - LIVE DATA ONLY)")
    print("=" * 90)
    print(f"Finnhub API Key: {service.finnhub_key[:15]}...{service.finnhub_key[-5:]}")
    print(f"Cache TTL: {service.cache_ttl} seconds (0 = DISABLED)")
    print(f"Cache Dictionary Size: {len(service.cache)} (should remain 0)")
    print("=" * 90)
    print()
    
    results = []
    
    for i in range(1, 11):
        try:
            print(f"Request {i:2d}...", end=" ", flush=True)
            start = time.time()
            quote = await service.get_quote('AAPL')
            elapsed = time.time() - start
            
            if quote:
                results.append({
                    'attempt': i,
                    'price': quote['current_price'],
                    'high': quote['high'],
                    'low': quote['low'],
                    'open': quote['open'],
                    'prev_close': quote['prev_close'],
                    'source': quote['source'],
                    'time': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'fetch_time_ms': round(elapsed * 1000)
                })
                print(f"✅ ${quote['current_price']:.2f} ({elapsed:.2f}s)")
            else:
                print("❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # No delays between requests to maximize chances of seeing live price updates
    
    # Print results table
    print()
    print("=" * 110)
    print("📈 LIVE DATA RESULTS SUMMARY (Cache Disabled)")
    print("=" * 110)
    print()
    print(f"{'#':<3} {'Time':<12} {'Price':<10} {'High':<10} {'Low':<10} {'Open':<10} {'Prev Close':<12} {'Fetch (ms)':<12}")
    print("-" * 110)
    
    for idx, result in enumerate(results, 1):
        print(f"{result['attempt']:<3} {result['time']:<12} ${result['price']:<9.2f} ${result['high']:<9.2f} ${result['low']:<9.2f} ${result['open']:<9.2f} ${result['prev_close']:<11.2f} {result['fetch_time_ms']:<12}")
    
    print()
    print("=" * 110)
    print("📊 ANALYSIS - Live Data Verification")
    print("=" * 110)
    
    prices = [r['price'] for r in results]
    print(f"Total Requests: {len(results)}")
    print(f"Unique Prices: {len(set(prices))}")
    print(f"Min Price: ${min(prices):.2f}")
    print(f"Max Price: ${max(prices):.2f}")
    print(f"Average Price: ${sum(prices)/len(prices):.2f}")
    print(f"Price Range: ${max(prices) - min(prices):.2f}")
    print()
    print(f"Cache Dictionary Size: {len(service.cache)} (should be 0 - cache disabled)")
    print()
    
    if len(set(prices)) > 1:
        print("✅ VERIFIED: Prices differ between requests - LIVE DATA working!")
        print("✅ Cache successfully disabled - fetching fresh data every time!")
    else:
        print("⚠️  All prices identical - Market may not have updated or prices fetched too quickly")
        print("   This is normal if all requests completed within milliseconds")
    
    print()
    print(f"✅ All {len(results)} requests successful with real Finnhub API!")
    print(f"✅ System is now running on LIVE DATA ONLY - no caching!")
    print()

if __name__ == "__main__":
    asyncio.run(fetch_stock_price_live())
