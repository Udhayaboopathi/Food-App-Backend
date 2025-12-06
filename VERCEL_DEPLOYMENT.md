# Vercel Deployment Guide for EatUpNow Backend

## ⚠️ Important Notes

**SQLite Database Issue:**
Vercel's serverless functions are stateless and ephemeral. SQLite with file storage **will not work** on Vercel because:
- Each serverless invocation starts fresh
- File system is read-only (except `/tmp`)
- Database file resets on each request

## Recommended Solutions

### Option 1: Use a Cloud Database (Recommended)
Switch to a managed database like:
- **PostgreSQL**: Neon, Supabase, Railway, or Vercel Postgres
- **MySQL**: PlanetScale, Railway
- **MongoDB**: MongoDB Atlas

Update `DATABASE_URL` in your environment variables to the cloud database connection string.

### Option 2: Deploy to a Different Platform
For SQLite support, use:
- **Railway** (already have `railway.json` configured)
- **Render**
- **Fly.io**
- **DigitalOcean App Platform**

## Deploy to Vercel (with limitations)

### Prerequisites
1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

### Deployment Steps

1. **Set Environment Variables** in Vercel Dashboard:
   - `SECRET_KEY`
   - `DATABASE_URL` (must be a cloud database URL)
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `REFRESH_TOKEN_EXPIRE_DAYS`
   - `CORS_ORIGINS`

2. **Deploy**:
   ```bash
   vercel --prod
   ```

### Current Configuration
- ✅ `vercel.json` created
- ✅ `.vercelignore` created
- ✅ `api/index.py` entry point created
- ✅ App modified for serverless compatibility
- ⚠️ SQLite will not persist data on Vercel

## Alternative: Deploy to Railway (Recommended for SQLite)

Railway supports SQLite with persistent storage:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

Your `railway.json` is already configured!

## File Uploads on Vercel

File uploads to local storage won't persist. Consider using:
- **Cloudinary**
- **AWS S3**
- **Vercel Blob Storage**
- **Uploadcare**

## Next Steps

**For Vercel Deployment:**
1. Migrate to PostgreSQL/MySQL
2. Set up cloud storage for images
3. Update `DATABASE_URL` environment variable
4. Deploy with `vercel --prod`

**For Railway Deployment (Easier):**
1. No code changes needed
2. Just run `railway up`
3. SQLite and file uploads work out of the box
