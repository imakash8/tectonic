import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FINNHUB_API_KEY')

print(f"Testing Finnhub API Key: {api_key}")
print("-" * 50)

url = "https://finnhub.io/api/v1/quote"
params = {
    "symbol": "AAPL",
    "token": api_key
}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        if 'c' in data and data['c']:
            print(f"✅ API KEY IS VALID")
            print(f"✅ AAPL Current Price: ${data['c']}")
            print(f"   High: ${data.get('h', 'N/A')}")
            print(f"   Low: ${data.get('l', 'N/A')}")
            print(f"   Open: ${data.get('o', 'N/A')}")
            print(f"   Previous Close: ${data.get('pc', 'N/A')}")
        else:
            print(f"⚠️ API returned 200 but no price data")
            print(f"Response: {data}")
    else:
        print(f"❌ API KEY IS INVALID or EXPIRED")
        print(f"Error Response: {data}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
