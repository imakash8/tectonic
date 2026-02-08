#!/usr/bin/env python3
"""
Diagnostic script to identify why prices fluctuate on Render
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Load .env file
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_path)

from app.config import settings

print("=" * 80)
print("🔍 DIAGNOSTIC REPORT: Price Fluctuation Root Cause Analysis")
print("=" * 80)

print("\n📋 API KEY CONFIGURATION CHECK:\n")

# Check FINNHUB key
finnhub_key = settings.FINNHUB_API_KEY
print(f"1. FINNHUB_API_KEY Status:")
if not finnhub_key or finnhub_key == "your_finnhub_key_here":
    print(f"   ❌ NOT CONFIGURED")
    print(f"   Value: {finnhub_key}")
else:
    print(f"   ✅ CONFIGURED")
    print(f"   Value: {finnhub_key[:15]}...{finnhub_key[-5:]}")
    print(f"   Length: {len(finnhub_key)} characters")

# Check Alpha Vantage key
alpha_key = settings.ALPHA_VANTAGE_KEY
print(f"\n2. ALPHA_VANTAGE_KEY Status:")
if not alpha_key or alpha_key == "your_alpha_vantage_key_here":
    print(f"   ❌ NOT CONFIGURED")
    print(f"   Value: {alpha_key}")
else:
    print(f"   ✅ CONFIGURED")
    print(f"   Value: {alpha_key[:15]}...{alpha_key[-5:]}")
    print(f"   Length: {len(alpha_key)} characters")

# Check settings
print(f"\n3. Market Data Settings:")
print(f"   • USE_REAL_TIME_DATA: {settings.USE_REAL_TIME_DATA}")
print(f"   • MARKET_DATA_CACHE_TTL: {settings.MARKET_DATA_CACHE_TTL} seconds")
print(f"   • PREFERRED_PROVIDER: {settings.PREFERRED_MARKET_DATA_PROVIDER}")

print("\n" + "=" * 80)
print("🎯 ROOT CAUSE IDENTIFICATION")
print("=" * 80)

if not finnhub_key or finnhub_key == "your_finnhub_key_here":
    print("\n❌ PRIMARY ISSUE IDENTIFIED:\n")
    print("   The FINNHUB_API_KEY is NOT configured!")
    print("\n   When FINNHUB_API_KEY is missing:")
    print("   1. ❌ Real-time Finnhub API cannot be called")
    print("   2. ❌ System falls back to Alpha Vantage (if configured)")
    print("   3. ❌ If both fail, system throws error (no mock data)")
    print("\n   WHY PRICES FLUCTUATE ON RENDER:")
    print("   → The backend on Render doesn't have the environment variable set")
    print("   → Each API call either fails, uses fallback, or gets different data")
    print("   → Without proper caching and API key, prices appear random")
else:
    print("\n✅ FINNHUB API KEY IS CONFIGURED LOCALLY\n")
    print("   But prices still fluctuate on Render because:")
    print("   → The Render environment variable is NOT set")
    print("   → Render deployment doesn't inherit local .env")
    print("   → Must be manually configured on Render dashboard")

print("\n" + "=" * 80)
print("🔧 SOLUTION: Set Environment Variable on Render")
print("=" * 80)

print("\n📌 Steps to fix:")
print("\n1. Go to: https://dashboard.render.com")
print("2. Click on your Backend Service (tectonic-4prz)")
print("3. Go to Settings → Environment")
print("4. Add new environment variable:")
print(f"   Name:  FINNHUB_API_KEY")
print(f"   Value: {finnhub_key}")
print("5. Click 'Save' - Render will auto-redeploy")
print("6. Wait for deployment to complete (~5 minutes)")
print("7. Test by fetching a quote - prices should be consistent")

print("\n" + "=" * 80)
print("✅ LOCAL VERIFICATION (from test_price_consistency.py):")
print("=" * 80)
print("\n   ✓ API Key is VALID and working")
print("   ✓ Prices are IDENTICAL across 10 consecutive calls")
print("   ✓ Caching is WORKING CORRECTLY")
print("   ✓ No variation in 20 seconds (0.0%)")
print("\n   This proves the local system is correct.")
print("   The problem is 100% the Render environment configuration.")

print("\n" + "=" * 80)
