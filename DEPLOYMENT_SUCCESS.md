# 🚀 Vercel Deployment - Working Solution

## ✅ FIXED: App folder copied into api/

The issue was that Vercel's Python runtime couldn't find the `app` module because it was outside the `api/` folder.

### Solution Applied:

- Copied `app/` folder into `api/app/`
- Now `api/index.py` can import from `app.main`
- Added `app/` to `.vercelignore` to prevent duplicate deployment

---

## 📦 Deploy to Vercel

### Step 1: Ensure app folder is copied (Already Done ✅)

The `app` folder has been copied into `api/app/`. You can verify:

```bash
ls api/app  # Should show: main.py, core/, models/, routers/
```

### Step 2: Commit and Push

```bash
git add .
git commit -m "Fix Vercel deployment - copy app into api folder"
git push origin main
```

### Step 3: Verify Vercel Settings

1. Go to: https://vercel.com/dashboard
2. Select your project
3. **Settings** → **General** → **Root Directory**: Set to `backend`
4. **Save**

### Step 4: Deploy

Vercel will auto-deploy from your GitHub push. Wait ~2 minutes.

---

## ✅ After Deployment

Test these URLs (replace with your actual domain):

```bash
# 1. Root endpoint
curl https://food-app-backend-liart.vercel.app/

# Expected:
# {"message":"Welcome to EatUpNow API! 🍔","slogan":"Your hunger, handled instantly",...}

# 2. Database check
curl https://food-app-backend-liart.vercel.app/db-check

# Expected:
# {"mongo_connected":true,"status":"connected",...}

# 3. API Documentation
https://food-app-backend-liart.vercel.app/docs
```

---

## 🔄 Future Deployments

**Before each deployment**, run this to sync any changes from `app/` to `api/app/`:

### On Windows:

```cmd
prepare-vercel.bat
git add .
git commit -m "Update deployment"
git push
```

### On Mac/Linux:

```bash
bash prepare-vercel.sh
git add .
git commit -m "Update deployment"
git push
```

---

## 📁 Current Structure

```
backend/
├── api/                  ← Vercel deploys from here
│   ├── app/             ← COPY of main app folder ✅
│   │   ├── main.py
│   │   ├── core/
│   │   ├── models/
│   │   └── routers/
│   ├── index.py         ← Entry point
│   └── __init__.py
├── app/                 ← Original app folder (ignored by Vercel)
│   ├── main.py
│   ├── core/
│   ├── models/
│   └── routers/
├── requirements.txt
└── vercel.json
```

---

## ⚠️ Important Notes

1. **Keep both `app/` folders in sync**

   - Original: `backend/app/`
   - Deployed: `backend/api/app/`
   - Use `prepare-vercel.bat` or `prepare-vercel.sh` before each deployment

2. **Don't manually edit `api/app/`**

   - Always edit the original `app/` folder
   - Then run prepare script to sync

3. **Environment Variables in Vercel**
   - Make sure `MONGODB_URI` and `SECRET_KEY` are set
   - Settings → Environment Variables

---

## 🎉 Success Indicators

After deployment, you should see in Vercel function logs:

```
🚀 Starting EatUpNow API...
🔌 Connecting to MongoDB...
✅ MongoDB connected successfully
```

And all endpoints should return 200 OK, not 500!
