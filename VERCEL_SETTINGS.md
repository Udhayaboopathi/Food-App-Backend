# ⚠️ CRITICAL: Vercel Project Settings

## The Error: `ModuleNotFoundError: No module named 'app.main'`

This means Vercel can't find your `app` folder.

---

## ✅ FIX: Update Vercel Project Settings

### Go to Vercel Dashboard:

1. **Sign in to Vercel:** https://vercel.com/dashboard
2. **Select your project** (food-app-backend)
3. Go to **Settings** (top menu)
4. Click **General** (left sidebar)

### Critical Setting:

**Root Directory:**

- Current: `backend` ❌ (This is WRONG if your repo structure is different)
- Should be: ` ` (empty/blank) ✅ **IF** you're deploying from the `backend` folder as the repository root

**OR**

- Should be: `backend` ✅ **IF** your GitHub repo has `frontend` and `backend` folders

---

## 📁 Check Your GitHub Repository Structure

### Option A: Backend is the root

```
your-repo/
├── api/
│   └── index.py
├── app/
│   ├── main.py
│   ├── core/
│   └── routers/
├── requirements.txt
└── vercel.json
```

**Vercel Root Directory:** ` ` (leave blank)

### Option B: Backend is a subfolder

```
your-repo/
├── frontend/
│   └── ...
├── backend/
│   ├── api/
│   │   └── index.py
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   └── routers/
│   ├── requirements.txt
│   └── vercel.json
```

**Vercel Root Directory:** `backend`

---

## ⚡ Quick Fix Steps

### 1. Check Your GitHub Repository

- Go to your GitHub repo
- Look at the file structure
- Determine if `backend` is root or a subfolder

### 2. Update Vercel Settings

1. Vercel Dashboard → Your Project → **Settings** → **General**
2. Find **Root Directory** section
3. Set it correctly based on your repo structure:
   - If backend IS the root: Leave **blank** or set to `.`
   - If backend is a subfolder: Set to `backend`
4. Click **Save**

### 3. Redeploy

1. Go to **Deployments** tab
2. Click **"..."** menu on latest deployment
3. Click **"Redeploy"**

---

## 🔍 If Still Failing - Check Build Logs

After redeploying, check the build logs:

1. Go to **Deployments**
2. Click on the latest deployment
3. Look for this section in logs:

```
Installing dependencies...
```

Should show:

```
Successfully installed fastapi beanie motor pymongo ...
```

Then look for:

```
Building...
```

Should complete without errors.

---

## 🎯 Expected Success

After correct configuration, you should see:

```
✓ Deployment successful
✓ Build completed
✓ Functions deployed
```

Then test:

- `https://your-app.vercel.app/` → JSON response ✅
- `https://your-app.vercel.app/db-check` → Database status ✅
- `https://your-app.vercel.app/docs` → Swagger UI ✅

---

## 🚨 Still Getting Errors?

### Check Function Logs:

1. Vercel Dashboard → Deployments → Click deployment
2. Click **"View Function Logs"**
3. Look for the actual error

### Common Issues:

**"No module named 'app'"**
→ Root Directory is wrong in Vercel settings

**"ModuleNotFoundError: No module named 'app.main'"**
→ Root Directory is wrong OR app folder not included in deployment

**"ModuleNotFoundError: No module named 'fastapi'"**
→ requirements.txt not found or not installed

---

## 📧 Share This Info:

To help debug, please share:

1. Your GitHub repository structure (screenshot of files)
2. Vercel Root Directory setting (screenshot)
3. Full build logs from Vercel
