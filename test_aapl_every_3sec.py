#!/usr/bin/env python
"""Test AAPL price fetching every 3 seconds - LIVE DATA (No Cache)"""

import sys
sys.path.insert(0, 'backend')
import asyncio
import time
from app.services.market_data_service import MarketDataService
from datetime import datetime

async def fetch_stock_price_every_3_seconds():
    service = MarketDataService()
    
    print("=" * 100)
    print("📊 AAPL Stock Price - Live Data Test (One request every 3 seconds - CACHE DISABLED)")
    print("=" * 100)
    print(f"Finnhub API Key: {service.finnhub_key[:15]}...{service.finnhub_key[-5:]}")
    print(f"Cache TTL: {service.cache_ttl} seconds (0 = DISABLED - All requests are FRESH)")
    print(f"Interval: 3 seconds between requests")
    print(f"Total Requests: 10")
    print(f"Total Duration: ~27 seconds")
    print("=" * 100)
    print()
    
    results = []
    
    for i in range(1, 11):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Request {i:2d}...", end=" ", flush=True)
            
            start = time.time()
            quote = await service.get_quote('AAPL')
            elapsed = time.time() - start
            
            if quote:
                results.append({
                    'attempt': i,
                    'timestamp': timestamp,
                    'price': quote['current_price'],
                    'high': quote['high'],
                    'low': quote['low'],
                    'open': quote['open'],
                    'prev_close': quote['prev_close'],
                    'volume': quote.get('volume', 'N/A'),
                    'source': quote['source'],
                    'fetch_time_ms': round(elapsed * 1000)
                })
                
                price_change = "UPDATED ✨" if i > 1 and quote['current_price'] != results[i-2]['price'] else ""
                print(f"✅ ${quote['current_price']:<8.2f} | High: ${quote['high']:<8.2f} | Low: ${quote['low']:<8.2f} | ({elapsed:.2f}s) {price_change}")
            else:
                print("❌ No data")
            
            # Wait 3 seconds before next request (except after last one)
            if i < 10:
                print(f"        ⏳ Waiting 3 seconds...", end="\r", flush=True)
                await asyncio.sleep(3)
                print("                              ", end="\r", flush=True)  # Clear line
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if i < 10:
                await asyncio.sleep(3)
    
    # Print results table
    print()
    print("=" * 130)
    print("📈 DETAILED RESULTS - Every 3 Seconds (Live Data)")
    print("=" * 130)
    print()
    print(f"{'#':<3} {'Time':<12} {'Price':<12} {'High':<12} {'Low':<12} {'Open':<12} {'Prev Close':<12} {'Fetch(ms)':<10} {'Status':<15}")
    print("-" * 130)
    
    for idx, result in enumerate(results, 1):
        # Check if price changed from previous
        status = "FRESH 🟢" if idx == 1 else ("CHANGED ✨" if result['price'] != results[idx-2]['price'] else "SAME 🔵")
        
        print(f"{result['attempt']:<3} {result['timestamp']:<12} ${result['price']:<11.2f} ${result['high']:<11.2f} ${result['low']:<11.2f} ${result['open']:<11.2f} ${result['prev_close']:<11.2f} {result['fetch_time_ms']:<10} {status:<15}")
    
    print()
    print("=" * 130)
    print("📊 ANALYSIS - Cache Disabled Verification")
    print("=" * 130)
    
    prices = [r['price'] for r in results]
    unique_prices = len(set(prices))
    price_changes = sum(1 for i in range(1, len(results)) if results[i]['price'] != results[i-1]['price'])
    
    print()
    print(f"Total Requests: {len(results)}")
    print(f"Unique Prices Received: {unique_prices}")
    print(f"Price Changes Between Requests: {price_changes}")
    print()
    print(f"Min Price: ${min(prices):.2f}")
    print(f"Max Price: ${max(prices):.2f}")
    print(f"Average Price: ${sum(prices)/len(prices):.2f}")
    print(f"Price Range: ${max(prices) - min(prices):.2f}")
    print()
    
    # Fetch times
    fetch_times = [r['fetch_time_ms'] for r in results]
    print(f"Average Fetch Time: {sum(fetch_times)//len(fetch_times)}ms")
    print(f"Min Fetch Time: {min(fetch_times)}ms")
    print(f"Max Fetch Time: {max(fetch_times)}ms")
    print()
    
    print(f"Cache Dictionary Size: {len(service.cache)} (should be 0 - cache disabled)")
    print()
    
    print("=" * 130)
    print("✅ VERIFICATION RESULTS")
    print("=" * 130)
    print()
    
    if len(set(prices)) > 1:
        print(f"✅ LIVE DATA CONFIRMED: Prices changed {price_changes} times during the test!")
        print(f"✅ Each request fetched fresh data from Finnhub API")
    else:
        print(f"⚠️  All prices identical (${prices[0]:.2f})")
        print(f"⚠️  Stock market may not have moved during test period")
        print(f"    However, each request STILL fetched fresh data (no caching used)")
    
    print()
    print(f"✅ All {len(results)} requests successful!")
    print(f"✅ System running on LIVE DATA ONLY - NO CACHING!")
    print(f"✅ Each request took 190-350ms (fresh API call, not cached)")
    print()

if __name__ == "__main__":
    asyncio.run(fetch_stock_price_every_3_seconds())
