# 🚀 VERCEL DEPLOYMENT FIX - Quick Guide

## ✅ What Was Fixed

### 1. Created Proper Vercel Entry Point

- **New file:** `api/index.py` - Vercel serverless function handler
- **Updated:** `vercel.json` - Points to correct entry point

### 2. Optimized Database Connection

- Added shorter timeout for Vercel (3 seconds instead of 5)
- Limited connection pool size to 1 for serverless
- Better error logging

### 3. Fixed Lifespan Management

- MongoDB connects on every function invocation (required for serverless)
- No connection closing in serverless mode (Vercel handles cleanup)

### 4. Added Deployment Files

- `.vercelignore` - Excludes unnecessary files
- Proper error handling for connection failures

---

## 🔧 CRITICAL: Environment Variables

**You MUST add these in Vercel Dashboard:**

1. Go to: https://vercel.com/dashboard
2. Select your project
3. Go to: **Settings** → **Environment Variables**
4. Add these TWO variables:

```
Name: MONGODB_URI
Value: mongodb+srv://udhaya:udhaya@udhaya.ibrprte.mongodb.net/eatupnow?retryWrites=true&w=majority
```

```
Name: SECRET_KEY
Value: 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

5. **IMPORTANT:** After adding variables, go to **Deployments** tab and click **"Redeploy"**

---

## 📤 Deploy Now

### Option 1: Push to GitHub (Recommended)

```bash
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

Vercel will auto-deploy from your GitHub repository.

### Option 2: Deploy via Vercel CLI

```bash
npm i -g vercel
cd backend
vercel --prod
```

---

## ✅ Verify Deployment

After deployment completes (wait ~2 minutes), test these URLs:

### 1. Root endpoint

```
https://your-app-name.vercel.app/
```

Should show: `"message": "Welcome to EatUpNow API! 🍔"`

### 2. Database check

```
https://your-app-name.vercel.app/db-check
```

Should show: `"mongo_connected": true`

### 3. API Documentation

```
https://your-app-name.vercel.app/docs
```

Should load Swagger UI (no 500 error!)

---

## 🐛 If Still Getting 500 Error

### Check Function Logs:

1. Go to Vercel Dashboard
2. Click your project
3. Go to **Deployments**
4. Click the latest deployment
5. Click **"View Function Logs"**
6. Look for errors

### Common Issues:

**Issue:** "MONGODB_URI not found"
**Fix:** Add environment variable and **redeploy**

**Issue:** "Module 'app' not found"
**Fix:** Make sure you deployed from the `backend` folder

**Issue:** "ServerSelectionTimeoutError"
**Fix:** MongoDB Atlas network access must allow 0.0.0.0/0 (already done ✅)

---

## 📁 Files Created/Modified

### New Files:

- ✅ `api/index.py` - Vercel entry point
- ✅ `.vercelignore` - Exclude files from deployment
- ✅ `VERCEL_FIX.md` - This file

### Modified Files:

- ✅ `vercel.json` - Fixed build configuration
- ✅ `app/main.py` - Optimized for serverless
- ✅ `app/core/database.py` - Better error handling + db_initialized flag

---

## ⚡ Why It Was Crashing

1. **Wrong entry point** - `vercel.json` pointed to `app/main.py` directly (doesn't work for Vercel)
2. **Missing environment variables** - MONGODB_URI not set in Vercel
3. **Connection timeout** - MongoDB connection took too long for serverless cold start
4. **No error isolation** - Connection failures crashed the entire app

## ✅ How It's Fixed

1. **Proper entry point** - `api/index.py` exports FastAPI app correctly
2. **Faster connection** - 3-second timeout for serverless
3. **Graceful degradation** - App starts even if MongoDB fails
4. **Health checks** - `/db-check` endpoint verifies database status

---

## 🎉 Next Steps After Successful Deployment

1. Update your frontend to use the Vercel URL
2. Test all API endpoints
3. (Optional) Add custom domain in Vercel settings

---

**Need help?** Check the function logs in Vercel Dashboard for detailed error messages.
