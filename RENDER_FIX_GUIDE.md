# How to Fix Login "Not Found" Error on Render - Step-by-Step Guide

## 🎯 Quick Fix (5-10 minutes)

### Step 1: Go to Render Dashboard
1. Open https://dashboard.render.com
2. Login to your account
3. Click on your project "tectonic" or "Tectonic Trading Platform"

### Step 2: Select Backend Service
1. Find "tectonic-backend" service in the services list
2. Click on it to open the service details

### Step 3: Set Environment Variables
1. Click on "Environment" tab on the left sidebar
2. You'll see a list of environment variables

#### Add/Update These Variables:

**Variable 1: FINNHUB_API_KEY**
- Key: `FINNHUB_API_KEY`
- Value: `d5mom81r01qj2afh5otgd5mom81r01qj2afh5ou0` (from your backend/.env)
- Click "Add"

**Variable 2: SECRET_KEY**
- Key: `SECRET_KEY`
- Value: `tectonic-trading-platform-secret-key-change-in-production` (from your backend/.env)
- Click "Add"

**Variable 3: ALPHA_VANTAGE_KEY (Optional)**
- Key: `ALPHA_VANTAGE_KEY`
- Value: `your_alpha_vantage_key_here` (if you have one, otherwise leave empty)
- Click "Add"

### Step 4: Verify All Variables Are Set
You should see these variables in the Environment section:
```
DATABASE_URL = postgresql://...  (auto-configured)
FINNHUB_API_KEY = d5mom81r01qj2af...
SECRET_KEY = tectonic-trading-platform-...
MARKET_DATA_CACHE_TTL = 0
ALLOWED_ORIGINS = https://tectonic-frontend.onrender.com
ENVIRONMENT = production
DEBUG = False
```

### Step 5: Deploy
1. Scroll up to the top of the page
2. Click the **"Redeploy"** button (or "Deploy latest commit")
3. Wait for the deployment to complete (you'll see a progress indicator)
4. Deployment takes 5-10 minutes

### Step 6: Verify It's Working
1. Wait for the "Deployed" status
2. Open a terminal and run:
```bash
curl https://tectonic-backend.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "Tectonic Trading Platform API"
}
```

If it's still showing 404, wait a few more minutes and try again.

### Step 7: Test Login Flow
1. Go to https://tectonic-frontend.onrender.com
2. Register a new account: `test@example.com` / `test1234`
3. You should see the dashboard
4. Click logout
5. Try to login with the same credentials
6. **Should work now!** ✅

---

## 📋 Detailed Screenshots Guide

### Finding Environment Variables Section
```
Dashboard.render.com 
  → Select "tectonic-backend" service
    → Left sidebar → "Environment"
      → Add/Edit environment variables
```

### What You're Looking For
The Environment section shows all key-value pairs. You need to add:
- FINNHUB_API_KEY
- SECRET_KEY
- ALPHA_VANTAGE_KEY (optional)

### Redeploy Button Location
- Top right corner of the service page
- Button says "Redeploy" or "Deploy latest commit"
- Click it to restart the backend service with new env vars

---

## ✅ Verification Steps

### Check 1: Health Endpoint
```bash
curl https://tectonic-backend.onrender.com/health
# Should return: {"status": "healthy", ...}
# NOT 404
```

### Check 2: Register
```bash
curl -X POST https://tectonic-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "test1234",
    "full_name": "Test User"
  }'
# Should return: {"access_token": "...", ...}
# NOT 404
```

### Check 3: Login
```bash
curl -X POST https://tectonic-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "test1234"
  }'
# Should return: {"access_token": "...", ...}
# NOT 404
```

### Check 4: Login After Logout
1. Register on frontend
2. See dashboard
3. Click Logout
4. Login again
5. Should work! ✅

---

## 🔧 Troubleshooting

### Problem: Still Getting 404
**Solution:**
1. Make sure you clicked "Redeploy" (not just saved env vars)
2. Wait 10-15 minutes for deployment to complete
3. Check the Deployment Logs (click "Logs" tab) for errors
4. Make sure FINNHUB_API_KEY value is correct (copy from backend/.env)

### Problem: Deployment Fails
**Solution:**
1. Check Logs tab for error messages
2. Verify FINNHUB_API_KEY is set with correct value
3. Verify SECRET_KEY is set
4. Try redeploy again

### Problem: Backend Returns 500 Error
**Solution:**
1. Check that DATABASE_URL is set (should be auto-configured)
2. Verify FINNHUB_API_KEY is a valid 40-character string
3. Check logs for specific error

### Problem: All API Calls Return 404
**Solution:**
1. Check that x-render-routing header is NOT "no-server"
2. Wait longer for deployment
3. Try clearing browser cache
4. Try accessing /health endpoint directly

---

## 🔑 Environment Variables Quick Reference

Copy these from `backend/.env` file:

```bash
# From backend/.env:
FINNHUB_API_KEY=d5mom81r01qj2afh5otgd5mom81r01qj2afh5ou0
SECRET_KEY=tectonic-trading-platform-secret-key-change-in-production
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

Paste the values (right side of =) into Render Environment Variables.

---

## ⏱️ Timeline

| Action | Time |
|--------|------|
| Set environment variables | 2 minutes |
| Click Redeploy | 1 minute |
| Deployment build & deploy | 5-10 minutes |
| Verification test | 1 minute |
| **Total** | **~10-15 minutes** |

---

## ✨ After Fix Is Complete

Once backend is running:
- ✅ Users can register
- ✅ Users can login
- ✅ Users can logout
- ✅ Users can login again after logout
- ✅ Live stock prices load
- ✅ All features work

---

## 💡 Key Points

1. **Environment variables must be set BEFORE redeploy**
2. **Redeploy button restarts the service with new variables**
3. **Deployment takes 5-10 minutes** - be patient
4. **Backend must have these to start:**
   - FINNHUB_API_KEY (to fetch stock prices)
   - SECRET_KEY (to sign JWT tokens)
5. **After redeploy, backend should respond** to all API requests

---

## 🆘 Still Not Working?

If following these steps doesn't fix it:
1. Check Render logs for error messages
2. Verify environment variable values are correct
3. Make sure you clicked "Redeploy" button
4. Wait 15+ minutes for full deployment
5. Try clearing browser cache and cookies
6. Check if FINNHUB_API_KEY format is correct (40 chars, alphanumeric)

