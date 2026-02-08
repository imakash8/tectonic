# Render Frontend Deployment - Detailed Step-by-Step Guide

## PART 1: BEFORE YOU START

### Prerequisites:
1. ✅ Backend deployed and running on Render
2. ✅ Your backend URL (from Render dashboard)
3. ✅ GitHub repository pushed to main branch
4. ✅ Render account logged in at https://dashboard.render.com

---

## PART 2: STEP 1-3 (Quick Review)

### Step 1: Go to Render Dashboard
```
1. Open: https://dashboard.render.com
2. Look for "New +" button in top right corner
3. Click on it
4. A dropdown menu appears with options:
   - Web Service
   - Static Site  ← SELECT THIS
   - PostgreSQL
   - Redis
   - etc.
5. Click "Static Site"
```

### Step 2: Connect Your Repository
```
After clicking "Static Site":
1. Page shows "Connect a repository"
2. Look for your GitHub account name
3. Find your repository: imakash8/tectonic
4. Click on it to select
5. Click "Connect" button
```

### Step 3: Configure Frontend Settings

**This is the most important page. You'll see:**

```
┌─────────────────────────────────────────────┐
│ Create a new Static Site                    │
├─────────────────────────────────────────────┤
│                                             │
│ NAME: [____________________]                │
│  → Type: tectonic-frontend                  │
│                                             │
│ BRANCH: [____________________]              │
│  → Type: main                               │
│                                             │
│ BUILD COMMAND: [____________________]       │
│  → Copy/paste this EXACTLY:                 │
│     cd frontend && npm install &&           │
│     npm run build                           │
│                                             │
│ PUBLISH DIRECTORY: [____________________]   │
│  → Type: frontend/dist                      │
│                                             │
└─────────────────────────────────────────────┘
```

**Detailed Fill-In Instructions:**

**Field 1: NAME**
- Current: (empty or default)
- Change to: `tectonic-frontend`
- Why: This is your site's identifier on Render

**Field 2: BRANCH**
- Current: (shows available branches)
- Select: `main`
- Why: Your code is on the main branch

**Field 3: BUILD COMMAND**
- Current: (empty)
- Paste: `cd frontend && npm install && npm run build`
- What it does:
  - `cd frontend` = Navigate to frontend folder
  - `npm install` = Install dependencies from package.json
  - `npm run build` = Build React app for production (creates `dist` folder)

**Field 4: PUBLISH DIRECTORY**
- Current: (empty)
- Type: `frontend/dist`
- What it is: The folder that will be served as your website
  - After `npm run build`, React creates a `dist` folder
  - Render will serve all files from `dist` as a static website

---

## PART 3: STEP 4 - ADD ENVIRONMENT VARIABLE (DETAILED)

**This is the critical step** - it tells your frontend where to find the backend API.

### Finding the Environment Variables Section

After you fill in the 4 fields above, scroll down the page:

```
┌─────────────────────────────────────────────┐
│ [Already filled in above]                   │
│                                             │
│ [Scroll down...]                            │
│                                             │
│ ENVIRONMENT: (or "Advanced")                │
│ ↓ Click here to expand                      │
└─────────────────────────────────────────────┘
```

### Option A: If you see "ENVIRONMENT" section

```
┌─────────────────────────────────────────────┐
│ ENVIRONMENT                                 │
├─────────────────────────────────────────────┤
│                                             │
│ [+ Add Environment Variable] button         │
│                                             │
│ (or might show existing variables)          │
│                                             │
└─────────────────────────────────────────────┘
```

### Option B: If you see "Advanced"

```
Look for a section called:
- "Advanced"
- "Environment" 
- "Settings"

Click on it to expand
```

### Adding the Environment Variable

**Once you find the Environment section:**

1. Click **"+ Add Environment Variable"** button (or similar)

2. A form appears:
```
┌─────────────────────────────────────────────┐
│ Add Environment Variable                    │
├─────────────────────────────────────────────┤
│                                             │
│ KEY: [____________________]                 │
│                                             │
│ VALUE: [____________________]               │
│                                             │
│ [Add]  [Cancel]                             │
│                                             │
└─────────────────────────────────────────────┘
```

3. **Fill in KEY field:**
   - Type: `VITE_API_BASE_URL`
   - This is the variable name (must be exact - Vite requires VITE_ prefix)

4. **Fill in VALUE field:**
   - **IMPORTANT**: You need your backend URL first
   - Pattern: `https://your-backend-name.onrender.com/api`
   
   **How to find your backend URL:**
   
   a) In Render dashboard, look at the left sidebar
   b) Find your backend service (likely called "tectonic-backend")
   c) Click on it
   d) Look for URL field at the top (shows something like):
      ```
      https://tectonic-backend-xxxxx.onrender.com
      ```
   e) Copy that URL
   f) Add `/api` to the end
   g) Paste in the VALUE field
   
   **Example:**
   ```
   If backend URL is: https://tectonic-backend-abc123.onrender.com
   Then VALUE should be: https://tectonic-backend-abc123.onrender.com/api
   ```

5. Click **"Add"** button

6. The variable should now appear in a list:
```
┌─────────────────────────────────────────────┐
│ Environment Variables                       │
├─────────────────────────────────────────────┤
│                                             │
│ VITE_API_BASE_URL                          │
│ https://tectonic-backend-xxxx.onrender... │
│ [Edit] [Delete]                            │
│                                             │
└─────────────────────────────────────────────┘
```

---

## PART 4: STEP 5 - DEPLOY (DETAILED)

### Finding the Deploy Button

After you:
- ✅ Filled in NAME: `tectonic-frontend`
- ✅ Filled in BRANCH: `main`
- ✅ Filled in BUILD COMMAND: `cd frontend && npm install && npm run build`
- ✅ Filled in PUBLISH DIRECTORY: `frontend/dist`
- ✅ Added VITE_API_BASE_URL environment variable

**Scroll to the bottom of the page:**

```
┌─────────────────────────────────────────────┐
│ [All your settings above]                   │
│                                             │
│ [Scroll down to bottom...]                  │
│                                             │
│                                             │
│ [Create Static Site]  button (blue)         │
│ OR                                          │
│ [Deploy]  button (blue)                     │
│                                             │
└─────────────────────────────────────────────┘
```

### Click the Deploy Button

1. Look for a **blue button** that says one of:
   - "Create Static Site"
   - "Deploy"
   - "Create"
   - "Deploy Now"

2. **Click it once** (don't click multiple times)

3. **Page will change** - you'll see:
```
┌─────────────────────────────────────────────┐
│ tectonic-frontend                          │
│                                             │
│ Status: Building...                         │
│                                             │
│ Build in progress                           │
│ [Progress bar ████░░░░░░ 40%]               │
│                                             │
│ Logs:                                       │
│ > npm install                               │
│ > npm run build                             │
│ ...                                         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## PART 5: WAITING FOR BUILD (2-3 MINUTES)

### What Happens During Build

The build process will:
1. **npm install** (1-2 min)
   - Downloads all dependencies from package.json
   - Creates node_modules folder
   - Shows: `added 500+ packages`

2. **npm run build** (30-60 sec)
   - Compiles React code to optimized HTML/CSS/JS
   - Creates `frontend/dist` folder
   - Shows: `Build completed successfully`
   - Shows: `dist/index.html`

3. **Upload to Render** (30 sec)
   - Renders servers receive built files
   - Configures web server
   - Shows: `Deployment completed`

### What to Look For in Logs

**Good signs:**
```
✓ npm install completed successfully
✓ npm run build completed
✓ Built files: 15 files, 250KB
✓ Deployment URL: https://tectonic-frontend-xxxx.onrender.com
✓ Status: Live
```

**Bad signs** (if you see these, check settings):
```
✗ frontend/dist not found → BUILD COMMAND wrong
✗ Cannot find package.json → PUBLISH DIRECTORY wrong
✗ npm ERR! → Missing dependencies in package.json
✗ Port binding error → Rare, usually fine
```

---

## PART 6: AFTER DEPLOYMENT COMPLETES

### Success Page

When build is complete, you'll see:

```
┌─────────────────────────────────────────────┐
│ tectonic-frontend                          │
│                                             │
│ Status: ✓ Active/Live                      │
│                                             │
│ URL:                                        │
│ https://tectonic-frontend-abc123.onrender.com
│                                             │
│ [Open Site] button (blue)                   │
│                                             │
│ Build: Completed at 2026-02-08 16:55:00     │
│ Logs: [View Logs]                           │
│                                             │
└─────────────────────────────────────────────┘
```

### Click "Open Site"

1. **Click the blue "Open Site" button**
2. Your React app will load in a new tab
3. You should see the **Login page**

```
Expected:
┌─────────────────────────────────────────────┐
│         Tectonic Trading Platform           │
│                                             │
│         Email: [____________]               │
│         Password: [____________]            │
│                                             │
│         [Login]                             │
│         [Register]                          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## PART 7: VERIFY FRONTEND WORKS

### Test 1: Check Page Loads
- ✅ See Tectonic Trading Platform login page
- ✅ No error messages in browser console (F12)

### Test 2: Check Backend Connection
1. Open browser **Developer Tools** (F12)
2. Go to **Network** tab
3. Try to login with:
   - Email: `test@example.com`
   - Password: `testpassword`
4. Look for API calls in Network tab
5. Should see requests to: `https://tectonic-backend-xxxx.onrender.com/api/...`

### Test 3: Full Workflow
1. Click **Register** (if needed)
2. Create a test account
3. Go to **Portfolio** → **Create Portfolio**
4. Go to **Trading Floor**
5. Try to create a trade:
   - Symbol: AAPL
   - Type: BUY
   - Quantity: 10
   - Price: 150.00
6. Click **Execute Trade**
7. Should see validation gates show **Pass** or **Fail**

---

## TROUBLESHOOTING

### Problem 1: Build Failed
**Error**: "frontend/dist not found"
**Fix**: Check BUILD COMMAND is exactly:
```
cd frontend && npm install && npm run build
```

### Problem 2: Frontend Loads But White Screen
**Cause**: VITE_API_BASE_URL not set or wrong
**Fix**:
1. Open Browser DevTools (F12)
2. Check **Console** tab for errors
3. Look for: `Cannot connect to http://localhost...`
4. Go back to Render → Edit settings
5. Verify VITE_API_BASE_URL is set correctly
6. Click **Save** and **Redeploy**

### Problem 3: Login Not Working
**Cause**: Backend URL wrong or backend not responding
**Fix**:
1. In browser, check Network tab (F12)
2. See if login request is being sent
3. Check response status code
4. If 0 or timeout: Backend URL is wrong
5. If 404: Endpoint doesn't exist
6. If 500: Backend error (check backend logs)

### Problem 4: CORS Error in Console
**Error**: "Access to XMLHttpRequest blocked by CORS policy"
**Fix**:
1. Go to Render backend settings
2. Check ALLOWED_ORIGINS includes frontend URL
3. Should have: `https://tectonic-frontend-xxxx.onrender.com`
4. Redeploy backend

---

## SUMMARY CHECKLIST

### Before Clicking Deploy:
- [ ] NAME: `tectonic-frontend`
- [ ] BRANCH: `main`
- [ ] BUILD COMMAND: `cd frontend && npm install && npm run build`
- [ ] PUBLISH DIRECTORY: `frontend/dist`
- [ ] VITE_API_BASE_URL: Set to your backend API URL
- [ ] Backend service URL: Confirmed and working

### After Deployment:
- [ ] Status shows "Active" or "Live"
- [ ] Deployment took 2-3 minutes
- [ ] Click "Open Site" button
- [ ] Login page appears
- [ ] Try test login

### If Something Goes Wrong:
- [ ] Check logs in Render (Logs tab)
- [ ] Check browser console (F12)
- [ ] Verify environment variable is set
- [ ] Verify backend URL is correct and accessible
- [ ] Try rebuilding (look for Rebuild button in Render)

---

## NEXT STEPS AFTER DEPLOYMENT

1. **Share frontend URL with clients/stakeholders**
   - URL: `https://tectonic-frontend-xxxx.onrender.com`

2. **Collect feedback** on functionality

3. **Set up PostgreSQL database** (instead of SQLite)
   - For production data persistence

4. **Configure GitHub Actions** to auto-deploy on git push
   - Render auto-deploys on main branch pushes

5. **Set up alerts/monitoring** for uptime

---

## QUESTIONS?

If you get stuck:
1. Share the **exact error message** from Logs tab
2. Share what you see in browser console (F12)
3. Confirm backend is running and accessible
4. Check all environment variables are set correctly

Good luck! 🚀
