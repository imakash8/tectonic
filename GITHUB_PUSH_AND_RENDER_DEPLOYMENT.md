# GitHub Push & Render Deployment Guide

Complete step-by-step instructions to push your Tectonic Trading Platform to GitHub and deploy on Render.

---

## PART 1: PUSH CODE TO GITHUB

### Step 1: Open Terminal and Navigate to Project

```bash
cd /Users/akashkumar/Desktop/Toptal\ project
```

Verify you're in the correct directory:
```bash
pwd
# Should output: /Users/akashkumar/Desktop/Toptal project

ls
# Should show: backend/ frontend/ docker-compose.yml README.md etc.
```

### Step 2: Initialize Git (If Not Already Done)

Check if git is initialized:
```bash
git status
```

If you see "fatal: not a git repository", initialize:
```bash
git init
```

### Step 3: Add Remote Repository

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub details:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

**Example:**
```bash
git remote add origin https://github.com/akashkumar/tectonic-trading.git
```

Verify the remote:
```bash
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (fetch)
# origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (push)
```

### Step 4: Check Git Status

```bash
git status
```

This shows all files that need to be added.

### Step 5: Add All Files to Staging

```bash
git add .
```

Verify files are staged:
```bash
git status
# Should show green "Changes to be committed"
```

### Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: Tectonic Trading Platform MVP"
```

### Step 7: Push to GitHub

**First push (sets upstream):**
```bash
git branch -M main
git push -u origin main
```

**Subsequent pushes:**
```bash
git push
```

### Step 8: Verify on GitHub

1. Open https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
2. You should see all your files uploaded
3. Check the commits tab to see your initial commit

---

## PART 2: DEPLOY TO RENDER

### Step 1: Create Render Account

1. Go to **https://render.com**
2. Click **Sign Up**
3. Choose **"Sign up with GitHub"** (easiest)
4. Authorize GitHub access
5. Complete account setup

### Step 2: Connect GitHub Repository

1. Go to https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**
4. Select **"Connect a repository"**
5. Find your repository: `YOUR_USERNAME/YOUR_REPO_NAME`
6. Click **"Connect"**

### Step 3: Configure Backend Service

**Basic Settings:**
- **Name**: `tectonic-backend`
- **Environment**: `Python 3`
- **Region**: `Oregon` (or closest to you)
- **Branch**: `main`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Settings:**
1. Scroll down to **Environment**
2. Add these environment variables:

```
DATABASE_URL = sqlite:///./test.db
SECRET_KEY = your-secret-key-here-change-this-in-production
FINNHUB_API_KEY = your-finnhub-api-key
ALLOWED_ORIGINS = http://localhost:5173,https://your-frontend-url.onrender.com
DEBUG = false
DEBUG_MODE = false
MARKET_DATA_CACHE_TTL = 30
```

**Replace with your actual values:**
- `SECRET_KEY`: Generate random string (e.g., `openssl rand -base64 32`)
- `FINNHUB_API_KEY`: Your API key from Finnhub
- `ALLOWED_ORIGINS`: Will update after frontend is deployed

### Step 4: Deploy Backend

1. Click **"Create Web Service"**
2. Wait for build to complete (3-5 minutes)
3. You'll see a URL like `https://tectonic-backend.onrender.com`
4. Test it: Visit `https://tectonic-backend.onrender.com/docs`
   - Should see FastAPI Swagger documentation
5. **Copy this URL** for frontend configuration

### Step 5: Configure Frontend Service

1. Go back to https://dashboard.render.com
2. Click **"New +"** button
3. Select **"Static Site"**
4. Select your GitHub repo again
5. Click **"Connect"**

**Settings:**
- **Name**: `tectonic-frontend`
- **Branch**: `main`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist`

**Environment Variables:**
1. Click **"Advanced"** (if available)
2. Add environment variable:
```
VITE_API_BASE_URL = https://tectonic-backend.onrender.com/api
```

### Step 6: Deploy Frontend

1. Click **"Create Static Site"**
2. Wait for build to complete (2-3 minutes)
3. You'll see a URL like `https://tectonic-frontend.onrender.com`
4. Test it: Visit the URL
   - Should see the login page
5. **Copy this URL** to update backend CORS

### Step 7: Update Backend CORS Settings

1. Go to backend service on Render dashboard
2. Click **"Environment"**
3. Update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS = https://tectonic-frontend.onrender.com
```
4. Click **"Deploy"** to rebuild backend

### Step 8: Test Full Application

1. Visit your frontend URL: `https://tectonic-frontend.onrender.com`
2. Should see login page
3. Try login with test account:
   - **Email**: `test@example.com`
   - **Password**: `testpassword`
   - (If not registered, click Register first)
4. Create a portfolio
5. Try executing a trade:
   - Symbol: `AAPL`
   - Quantity: `10`
   - Type: `buy`
   - Price: Enter current price
6. Check that validation gates show **Pass** or **Fail**
7. View portfolio to confirm trade was recorded

### Step 9: Verify Everything Works

**Backend API:**
- [ ] `https://tectonic-backend.onrender.com/docs` - Shows Swagger UI
- [ ] API responds without CORS errors
- [ ] Market data returns fresh quotes

**Frontend:**
- [ ] `https://tectonic-frontend.onrender.com` - Loads without errors
- [ ] Login/Register work
- [ ] Portfolio page loads
- [ ] Trading page loads
- [ ] Can create trades

**Integration:**
- [ ] Frontend communicates with backend
- [ ] Trades execute successfully
- [ ] Validation gates display correctly
- [ ] No console errors in browser DevTools

---

## PART 3: TROUBLESHOOTING

### Problem: "CORS Error" when submitting trade

**Solution:**
1. Go to backend service on Render
2. Check `ALLOWED_ORIGINS` includes frontend URL
3. Rebuild backend: Click **"Manual Deploy"**

### Problem: Backend shows "Build failed"

**Check logs:**
1. Click backend service
2. Click **"Logs"** tab
3. Look for error messages
4. Common issue: Missing API key in environment variables

**Fix:**
1. Add missing environment variables
2. Click **"Manual Deploy"**

### Problem: Frontend shows blank page

**Check browser console:**
1. Visit frontend URL
2. Press F12 (Developer Tools)
3. Click **Console** tab
4. Look for error messages
5. If API error: Check that `VITE_API_BASE_URL` is correct

### Problem: "Build command failed" on frontend

**Solution:**
1. Verify `build.sh` exists in project root
2. Check `frontend/package.json` has `build` script
3. Try building locally first:
```bash
cd frontend
npm install
npm run build
```

### Problem: Can't connect to database

**For SQLite (current):**
- Should work automatically
- Database file is created on first run

**When moving to PostgreSQL:**
1. Create PostgreSQL database on Render
2. Update `DATABASE_URL` in backend environment
3. Run migrations (if using Alembic)

---

## PART 4: PRODUCTION IMPROVEMENTS

### Optional: Add Database (PostgreSQL)

1. Go to Render dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Name: `tectonic-db`
4. Region: Same as backend
5. Create database
6. Copy connection string
7. Update backend `DATABASE_URL` with this string
8. Redeploy backend

### Optional: Setup Environment-Specific Files

**Create .env.local (git ignored):**
```bash
# backend/.env.local
SECRET_KEY=your-local-secret
FINNHUB_API_KEY=your-local-key
```

**Before pushing changes:**
```bash
git add .
git commit -m "Update configuration"
git push
```

### Optional: Setup GitHub Actions for Auto-Deploy

Render auto-deploys on every push to main. To disable:
1. Backend service → Settings → Deactivate auto-deploy
2. Make manual deploys instead

---

## QUICK REFERENCE: Common Commands

### Git Commands
```bash
# Check status
git status

# Add all files
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push

# Check remote
git remote -v

# View logs
git log --oneline
```

### View Logs in Render
1. Go to service dashboard
2. Click **"Logs"** tab (right side)
3. Scroll to see deployment progress and errors

### Restart Service in Render
1. Go to service
2. Click **"Manual Deploy"** button
3. Wait for rebuild

---

## SUMMARY CHECKLIST

### Before Pushing to GitHub
- [ ] All files are in project directory
- [ ] No sensitive keys in code (use .env)
- [ ] Git initialized: `git init`
- [ ] Remote added: `git remote -v`
- [ ] Files staged: `git add .`
- [ ] Initial commit created: `git commit`

### After Pushing to GitHub
- [ ] Check repository on GitHub.com
- [ ] Verify all files are visible
- [ ] Verify commit history shows your commit

### Before Deploying to Render
- [ ] GitHub repository is public (or private with GitHub auth)
- [ ] All environment variables are ready
- [ ] API keys are obtained (Finnhub)
- [ ] Backend and frontend URLs are correct

### After Deploying to Render
- [ ] Backend /docs endpoint accessible
- [ ] Frontend page loads without errors
- [ ] CORS is configured correctly
- [ ] Test login and trade execution
- [ ] Check browser console for errors

### After Everything Works
- [ ] Backend URL: `https://tectonic-backend.onrender.com`
- [ ] Frontend URL: `https://tectonic-frontend.onrender.com`
- [ ] Share frontend URL with clients
- [ ] Monitor logs for any issues

---

## NEXT STEPS

After successful deployment:

1. **Test with clients** - Share frontend URL
2. **Collect feedback** - What needs improvement?
3. **Phase 1 security fixes** - Add auth to endpoints (80 hours)
4. **Phase 3 AI/ML planning** - Start LLM fine-tuning strategy

For detailed technical documentation, see **PROJECT_DOCUMENTATION.md**

---

**Questions?** Check logs in Render dashboard or run local tests:
```bash
cd backend
python -m pytest tests/
```
