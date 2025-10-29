# Quick Start Guide - Deploying TeamUp to Render

## What Was Changed

### New Files Created:
1. **`build.sh`** - Render build script (installs deps, collects static, runs migrations)
2. **`render.yaml`** - Optional blueprint configuration for Render
3. **`runtime.txt`** - Specifies Python 3.11.0
4. **`DEPLOYMENT_GUIDE.md`** - Complete step-by-step deployment instructions
5. **`DEPLOYMENT_CHECKLIST.md`** - Handy checklist for deployment

### Modified Files:
1. **`requirements.txt`** - Added:
   - `psycopg2-binary>=2.9.9` (PostgreSQL)
   - `gunicorn>=21.2.0` (Production server)
   - `whitenoise>=6.6.0` (Static files)
   - `dj-database-url>=2.1.0` (Database URL parsing)

2. **`config/settings.py`** - Updated:
   - Added imports for `dj_database_url` and `os`
   - Added WhiteNoise middleware
   - Updated database config to use `DATABASE_URL` env var
   - Configured WhiteNoise for static files
   - Fixed static/media URLs

3. **`.env.example`** - Updated with PostgreSQL examples and cleaner format

---

## Next Steps (Quick Version)

### 1. Commit Your Changes
```bash
git add .
git commit -m "Configure for Render deployment with PostgreSQL"
git push origin render
```

### 2. On Render.com:

**Create Database:**
- New + → PostgreSQL → Free tier
- Name: `teamup-db`
- Copy the **Internal Database URL**

**Create Web Service:**
- New + → Web Service
- Connect your GitHub repo
- Branch: `render`
- Build: `./build.sh`
- Start: `gunicorn config.wsgi:application`
- Free tier

**Environment Variables:**
```
PYTHON_VERSION = 3.11.0
SECRET_KEY = [Generate]
DEBUG = False
DATABASE_URL = [Paste Internal DB URL]
GEMINI_API_KEY = [Your API key]
```

**Note:** ALLOWED_HOSTS is automatically detected from Render's environment!

### 3. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for first deployment
- Visit your URL!

### 4. Access Admin Panel
Default admin account (created automatically):
- Email: `admin@teamup.com`
- Password: `password`
- URL: `https://your-app.onrender.com/admin/`

**⚠️ Change the password after first login!**

---

## Important Notes

⚠️ **Free Tier Limitations:**
- App spins down after 15 min inactivity (30-50s cold start)
- PostgreSQL database expires after 90 days
- Uploaded files don't persist (use S3 for production)

✅ **Local Development:**
- Remove `DATABASE_URL` from `.env` to use SQLite locally
- All changes work both locally and in production

📖 **Full Details:**
- See `DEPLOYMENT_GUIDE.md` for comprehensive instructions
- Use `DEPLOYMENT_CHECKLIST.md` to track your progress

---

🚀 **You're all set! Your app is production-ready for Render.**
