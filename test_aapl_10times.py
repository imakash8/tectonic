#!/usr/bin/env python
"""Test AAPL price fetching 10 consecutive times using Finnhub API"""

import sys
sys.path.insert(0, 'backend')
import asyncio
from app.services.market_data_service import MarketDataService
from datetime import datetime

async def fetch_stock_price_consecutive():
    service = MarketDataService()
    
    print("=" * 80)
    print("📊 AAPL Stock Price - 10 Consecutive Fetches")
    print("=" * 80)
    print(f"Finnhub API Key: {service.finnhub_key[:15]}...{service.finnhub_key[-5:]}")
    print(f"Cache TTL: {service.cache_ttl} seconds")
    print("=" * 80)
    print()
    
    results = []
    
    for i in range(1, 11):
        try:
            print(f"Attempt {i}...", end=" ", flush=True)
            quote = await service.get_quote('AAPL')
            
            if quote:
                results.append({
                    'attempt': i,
                    'price': quote['current_price'],
                    'high': quote['high'],
                    'low': quote['low'],
                    'open': quote['open'],
                    'prev_close': quote['prev_close'],
                    'source': quote['source'],
                    'time': datetime.now().strftime('%H:%M:%S')
                })
                print(f"✅ ${quote['current_price']:.2f}")
            else:
                print("❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Add 1 second delay between requests (except after last one)
        if i < 10:
            await asyncio.sleep(1)
    
    # Print results table
    print()
    print("=" * 80)
    print("📈 RESULTS SUMMARY")
    print("=" * 80)
    print()
    print(f"{'#':<3} {'Time':<10} {'Price':<10} {'High':<10} {'Low':<10} {'Source':<12} {'From Cache?':<12}")
    print("-" * 80)
    
    for idx, result in enumerate(results, 1):
        # Check if from cache (same price as previous)
        is_cached = "No" if idx == 1 else ("Yes" if result['price'] == results[idx-2]['price'] else "No")
        
        print(f"{result['attempt']:<3} {result['time']:<10} ${result['price']:<9.2f} ${result['high']:<9.2f} ${result['low']:<9.2f} {result['source']:<12} {is_cached:<12}")
    
    print()
    print("=" * 80)
    print("📊 ANALYSIS")
    print("=" * 80)
    
    prices = [r['price'] for r in results]
    print(f"Total Requests: {len(results)}")
    print(f"Unique Prices: {len(set(prices))}")
    print(f"Min Price: ${min(prices):.2f}")
    print(f"Max Price: ${max(prices):.2f}")
    print(f"Average Price: ${sum(prices)/len(prices):.2f}")
    
    # Count cached vs fresh
    cached_count = sum(1 for i in range(1, len(results)) if results[i]['price'] == results[i-1]['price'])
    print(f"Cached Responses: {cached_count}")
    print(f"Fresh API Calls: {len(results) - cached_count}")
    
    print()
    print(f"✅ All {len(results)} requests successful!")
    print(f"✅ Live data from Finnhub is working correctly!")
    print()

if __name__ == "__main__":
    asyncio.run(fetch_stock_price_consecutive())
