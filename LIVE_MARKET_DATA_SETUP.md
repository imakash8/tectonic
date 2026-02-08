# 📊 LIVE MARKET DATA - SETUP GUIDE FOR RENDER

## Problem

After logging in, when you try to:
- Search for a stock (e.g., AAPL)
- View live market data
- Execute a trade

You see error: **"Could not find data for AAPL"**

## Root Cause

The `FINNHUB_API_KEY` environment variable is **NOT configured on Render**.

### Why This Happens

1. ✅ **Local Development:** Works fine
   - API key is in `.env` file (git-ignored)
   - Backend loads it from `.env`
   - Real prices display correctly

2. ❌ **Render Production:** Doesn't work
   - `.env` file is not deployed (for security)
   - Render environment variables are empty
   - Backend can't authenticate with Finnhub
   - API calls fail → "Could not find data" error

---

## Solution: Configure Environment Variables on Render

### Step 1: Get Your Finnhub API Key

Your API key is in your local `.env` file:

```bash
# From your local machine (DO NOT commit this!)
cat backend/.env | grep FINNHUB_API_KEY
# Output: FINNHUB_API_KEY=d5mom81r01qj2afh5otgd5mom81r01qj2afh5ou0
```

### Step 2: Add to Render Dashboard

**Go to:** https://dashboard.render.com

1. **Select your Backend Service**
   - Service name: `tectonic-4prz` (or similar)

2. **Navigate to Environment**
   - Click: **Settings** → **Environment**

3. **Add Environment Variable**
   - Click: **"Add Environment Variable"**
   - **Name:** `FINNHUB_API_KEY`
   - **Value:** `d5mom81r01qj2afh5otgd5mom81r01qj2afh5ou0` (your API key)
   - Click: **"Save"**

4. **Wait for Auto-Redeployment**
   - Render will automatically redeploy your backend
   - Wait 5-10 minutes for deployment to complete
   - Check Render dashboard for green checkmark (deployed)

### Step 3: Verify It Works

1. Go to your app: https://tectonic-frontend.onrender.com
2. Log in with test credentials:
   - Email: `demo@example.com`
   - Password: `demo12345`

3. Go to **Trading** page
4. Search for a symbol: `AAPL`
5. You should see:
   - ✅ Live stock price (e.g., $278.13)
   - ✅ High/Low/Open prices
   - ✅ Company profile
   - ✅ Source: Finnhub

---

## What Gets Configured

### Before (❌ Not Configured on Render)
```
Render Backend Environment:
  FINNHUB_API_KEY = "" (empty)
  
User searches for AAPL:
  ↓
Backend tries to call Finnhub API:
  ↓
❌ No API key → Authentication fails
  ↓
Returns error: "Could not find data for AAPL"
  ↓
Frontend shows: "Could not find data"
```

### After (✅ Configured on Render)
```
Render Backend Environment:
  FINNHUB_API_KEY = "d5mom81r01qj2afh5otgd5mom81r01qj2afh5ou0"
  
User searches for AAPL:
  ↓
Backend calls Finnhub API with key:
  ↓
✅ Finnhub returns: {price: 278.13, high: 280.90, low: 276.92}
  ↓
Backend caches for 30 seconds
  ↓
Frontend receives real price: $278.13
  ↓
User sees live market data! 🎉
```

---

## Required API Keys

| Key | Purpose | Configured | Status |
|-----|---------|-----------|--------|
| **FINNHUB_API_KEY** | Real-time stock prices | ✅ Yes (d5mom81...) | 🔴 Missing on Render |
| ALPHA_VANTAGE_KEY | Fallback stock data (15min delayed) | ❌ No | Optional |
| ANTHROPIC_API_KEY | AI analysis | ❌ No | Optional |
| STRIPE_SECRET_KEY | Payments | ❌ No | Optional |

---

## How It Works Locally (Already Working)

When running locally (`npm run dev` / `python -m uvicorn`):

1. Flask/FastAPI loads `.env` file automatically
2. `FINNHUB_API_KEY` is set from `.env`
3. Backend can authenticate with Finnhub
4. Live prices are fetched and cached
5. Frontend displays prices correctly

**This is why it works locally but not on Render!**

---

## Troubleshooting

### Still Getting "Could not find data" After Setting Key?

**1. Check Deployment Status**
```
Go to Render Dashboard → Backend Service → Deployments
Look for green checkmark indicating successful deployment
```

**2. Clear Browser Cache**
```
Ctrl+Shift+Delete (Windows/Linux) or Cmd+Shift+Delete (Mac)
Clear "Cached Images and Files"
Hard refresh: Ctrl+F5 or Cmd+Shift+R
```

**3. Verify API Key is Set**
```
Render Dashboard → Settings → Environment
Look for FINNHUB_API_KEY in the list
```

**4. Check Render Logs**
```
Go to Render Dashboard → Logs
Search for "FINNHUB_API_KEY" or "market data"
Look for errors
```

### Getting Rate Limited?

If you see errors about rate limiting:
- Finnhub free tier allows ~60 requests/minute
- System caches prices for 30 seconds
- Multiple users hitting API simultaneously might cause rate limits
- Consider upgrading Finnhub plan for higher limits

---

## Security Best Practices

✅ **DO:**
- Store API keys in Render environment variables (not in code)
- Use `.gitignore` to prevent `.env` from being committed
- Rotate API keys periodically
- Use separate keys for dev/staging/production

❌ **DON'T:**
- Commit `.env` file to GitHub
- Put API keys in code
- Share API keys in Slack/email
- Use the same key across environments

---

## What Data Is Being Fetched

### Live Quote Endpoint: `/api/market/quote/AAPL`

**Request:**
```
GET https://tectonic-4prz.onrender.com/api/market/quote/AAPL
Authorization: Bearer {user_token}
```

**Response (With API Key):**
```json
{
  "symbol": "AAPL",
  "current_price": 278.13,
  "high": 280.90,
  "low": 276.92,
  "open": 277.13,
  "prev_close": 275.91,
  "volume": 45230000,
  "timestamp": "2026-02-08T20:30:00Z",
  "source": "finnhub"
}
```

**Response (Without API Key):**
```json
{
  "detail": "Unable to fetch real market data for AAPL. Please ensure FINNHUB_API_KEY or ALPHA_VANTAGE_KEY is properly configured."
}
```

---

## Company Profile Endpoint: `/api/market/profile/AAPL`

Same setup required. After configuring FINNHUB_API_KEY, you'll also see:
- Company name
- Industry
- Description
- Website
- Logo

---

## Market Overview Endpoint: `/api/market/overview`

Automatically fetches real-time data for market indices:
- **SPY** - S&P 500
- **QQQ** - Nasdaq
- **IWM** - Russell 2000
- **DXY** - Dollar Index
- **VIX** - Volatility Index

---

## Summary Checklist

- [ ] Copy FINNHUB_API_KEY from local `.env`
- [ ] Go to Render Dashboard → Backend Service → Settings
- [ ] Add FINNHUB_API_KEY environment variable
- [ ] Wait 5-10 minutes for deployment
- [ ] Clear browser cache (Ctrl+Shift+Delete)
- [ ] Hard refresh (Ctrl+F5)
- [ ] Log in and test Trading page
- [ ] Search for AAPL
- [ ] See live price displayed ✅

That's it! Your live market data should work perfectly now! 🚀
