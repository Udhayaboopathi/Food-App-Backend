# EatUpNow API - Vercel Deployment Guide

## Prerequisites Checklist

### ✅ 1. MongoDB Atlas Network Access

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Navigate to: **Network Access** (left sidebar)
3. Click **"Add IP Address"**
4. Select **"Allow Access from Anywhere"** (0.0.0.0/0)
5. Click **"Confirm"**

> ⚠️ This is required because Vercel serverless functions use dynamic IPs

---

## Vercel Deployment Steps

### ✅ 2. Push Code to GitHub

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### ✅ 3. Deploy to Vercel

#### Option A: Vercel CLI

```bash
npm i -g vercel
cd backend
vercel
```

#### Option B: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. **Root Directory:** Set to `backend`
5. Click **"Deploy"**

### ✅ 4. Configure Environment Variables in Vercel

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add the following variables:

| Name                          | Value                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------- |
| `MONGODB_URI`                 | `mongodb+srv://udhaya:udhaya@udhaya.ibrprte.mongodb.net/eatupnow?retryWrites=true&w=majority` |
| `SECRET_KEY`                  | `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7`                            |
| `ALGORITHM`                   | `HS256`                                                                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                                                                          |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                                                                                           |

3. Click **"Save"**
4. **Redeploy** the project to apply environment variables

---

## Validation Steps

### ✅ 5. Test Deployed API

After deployment completes, test these endpoints:

#### 1. Root Endpoint

```bash
curl https://your-project.vercel.app/
```

Expected response:

```json
{
  "message": "Welcome to EatUpNow API! 🍔",
  "slogan": "Your hunger, handled instantly",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### 2. Health Check

```bash
curl https://your-project.vercel.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "EatUpNow API",
  "version": "1.0.0"
}
```

#### 3. Database Connection Check (NEW)

```bash
curl https://your-project.vercel.app/db-check
```

Expected response (if MongoDB connected):

```json
{
  "mongo_connected": true,
  "status": "connected",
  "message": "MongoDB is operational"
}
```

Expected response (if MongoDB failed):

```json
{
  "mongo_connected": false,
  "status": "disconnected",
  "message": "MongoDB connection failed - check environment variables"
}
```

#### 4. API Documentation

Visit: `https://your-project.vercel.app/docs`

This should load the FastAPI Swagger UI without 500 error.

---

## Troubleshooting

### Issue: 500 Internal Server Error on /docs

**Cause:** MongoDB connection failed or environment variables missing

**Solution:**

1. Check `/db-check` endpoint first
2. If `mongo_connected: false`, verify:
   - MongoDB Atlas Network Access allows 0.0.0.0/0
   - MONGODB_URI is set in Vercel environment variables
   - Redeploy after adding environment variables

### Issue: Endpoints return "Database not initialized"

**Cause:** MongoDB connection timeout

**Solution:**

1. Check MongoDB Atlas cluster is active (not paused)
2. Verify MONGODB_URI connection string is correct
3. Test connection locally: `python -c "from pymongo import MongoClient; client = MongoClient('YOUR_URI'); print(client.admin.command('ping'))"`

### Issue: Some endpoints work, others return 500

**Cause:** Endpoints using database before initialization

**Solution:**

- Already fixed with `db_initialized` flag
- Database operations now fail gracefully

---

## Files Modified for Vercel Deployment

1. **vercel.json** (NEW) - Vercel configuration
2. **app/core/database.py** - Added `db_initialized` flag and graceful error handling
3. **app/main.py** - Added `/db-check` endpoint

---

## Local Testing Before Deployment

Test locally to ensure changes work:

```bash
cd backend
# Activate virtual environment
env\Scripts\activate  # Windows
# or
source env/bin/activate  # Linux/Mac

# Run server
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/db-check
curl http://localhost:8000/docs
```

---

## Expected Logs in Vercel

After successful deployment, you should see in Vercel function logs:

```
🚀 Starting EatUpNow API...
⚡ Running in Vercel serverless mode
✅ MongoDB connected successfully
```

If MongoDB fails:

```
🚀 Starting EatUpNow API...
⚡ Running in Vercel serverless mode
❌ MongoDB connection failed: ServerSelectionTimeoutError
⚠️ Please check your MONGODB_URI in environment variables
```

But the app will still start and `/docs` will work!

---

## Next Steps After Deployment

1. Update frontend API URL to point to Vercel deployment
2. Configure custom domain (optional)
3. Set up production environment variables separately
4. Enable Vercel Analytics (optional)

---

## Support

If you encounter issues:

1. Check Vercel function logs: Dashboard → Your Project → Deployments → View Function Logs
2. Test `/db-check` endpoint first
3. Verify MongoDB Atlas network access
4. Ensure environment variables are set and redeployed
