# Render Deployment Setup Guide

## Prerequisites
- Render.com account with a project
- GitHub repository connected to Render
- Finnhub API key (get from https://finnhub.io/)

## Environment Variables Required on Render Dashboard

### For Backend Service (tectonic-backend)
Set these in Render Dashboard under "Environment":

1. **FINNHUB_API_KEY** (Required)
   - Value: Your Finnhub API key from https://finnhub.io/
   - Why: Needed to fetch real-time stock prices

2. **SECRET_KEY** (Required)
   - Value: Generate a random secure string (e.g., `openssl rand -hex 32`)
   - Why: Used for JWT token signing and security

3. **ALPHA_VANTAGE_KEY** (Optional)
   - Value: Your Alpha Vantage API key (15-min delayed quotes)
   - Why: Fallback data source if Finnhub fails

4. **DATABASE_URL** (Auto-configured)
   - Automatically set from PostgreSQL database
   - Don't override manually

### Auto-configured by render.yaml
- `MARKET_DATA_CACHE_TTL=0` (Live data only)
- `ALLOWED_ORIGINS=https://tectonic-frontend.onrender.com`
- `ENVIRONMENT=production`
- `DEBUG=False`

## Deployment Steps

### Step 1: Connect GitHub to Render
1. Go to https://dashboard.render.com
2. Click "New Web Service"
3. Select GitHub repository: imakash8/tectonic
4. Render automatically reads render.yaml

### Step 2: Configure Backend Service
1. Service name: `tectonic-backend`
2. Environment: Python
3. Build Command: `cd backend && pip install -r requirements.txt`
4. Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Plan: Free (or Starter if needed)

### Step 3: Set Environment Variables
In the Render dashboard for tectonic-backend service:

```
FINNHUB_API_KEY = <your_finnhub_key>
SECRET_KEY = <random_secure_string>
ALPHA_VANTAGE_KEY = <your_alpha_vantage_key>  (optional)
```

### Step 4: Create PostgreSQL Database
1. Click "New PostgreSQL"
2. Name: `tectonic-db`
3. Database: `tectonic`
4. User: `tectonic_user`
5. Plan: Free
6. Region: Same as backend service

### Step 5: Deploy
1. Click "Deploy" or "Redeploy"
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors

## Verification

### Health Check
```bash
curl https://tectonic-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Tectonic Trading Platform API"
}
```

### Login Test
```bash
curl -X POST https://tectonic-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test1234"}'
```

Should return JWT tokens, not 404.

### Frontend Test
1. Navigate to https://tectonic-frontend.onrender.com
2. Register a new account
3. Verify you can login
4. Verify you can logout and login again
5. Verify stock prices load in dashboard

## Troubleshooting

### Backend Returns 404
- **Cause**: Service not running or crashed
- **Solution**: 
  1. Check Render logs for errors
  2. Verify all required environment variables are set
  3. Click "Redeploy" to restart service

### Backend Returns 500 Error
- **Cause**: Database connection error or missing API key
- **Solution**:
  1. Verify DATABASE_URL is set and PostgreSQL is running
  2. Verify FINNHUB_API_KEY is set with valid value
  3. Check logs for specific error message

### Login Says "Not Found"
- **Cause**: Frontend can't reach backend (API endpoint wrong)
- **Solution**:
  1. Verify frontend `.env.production` has: `VITE_API_BASE_URL=https://tectonic-backend.onrender.com/api`
  2. Verify backend health endpoint works (see Health Check above)
  3. Rebuild frontend: git push to trigger redeploy

### Users Can Register But Can't Login After Logout
- **Cause**: Backend service crashed after registration
- **Solution**:
  1. Check backend logs
  2. Verify all env variables are set
  3. Restart service by clicking "Redeploy"

## Auto-Redeployment
- When you push to GitHub main branch, Render automatically redeploys
- Check https://dashboard.render.com for deployment status
- Deployment takes 5-10 minutes

## Monitoring
- Keep Render dashboard open to monitor service health
- Check logs regularly for errors
- Set up alerts if available on your plan

## Database Migrations
First deployment initializes database automatically:
- Creates tables from SQLAlchemy models
- Seeds initial data (optional, see seed_test_users.py)

To seed test data:
```bash
cd backend
python scripts/seed_data.py
```

## Performance Tips
- Use Free tier for development/testing
- Upgrade to Starter tier for production
- Monitor API rate limits (Finnhub: 60 calls/min on free plan)
- Monitor database connections

## Security Notes
- Never commit API keys or secrets
- Use Render environment variables for sensitive data
- Rotate secrets regularly
- Use HTTPS endpoints only
- Keep ALLOWED_ORIGINS restricted to your domains
