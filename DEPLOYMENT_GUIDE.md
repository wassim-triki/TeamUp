# TeamUp Deployment Guide for Render

This guide will walk you through deploying your Django application to Render with PostgreSQL database.

## Prerequisites

- A GitHub account with your repository pushed
- A Render account (free tier available at https://render.com)
- Your Gemini API key

## Changes Made to the Codebase

The following changes have been made to prepare the application for Render deployment:

### 1. **requirements.txt** - Added production dependencies:
   - `psycopg2-binary>=2.9.9` - PostgreSQL adapter for Python
   - `gunicorn>=21.2.0` - WSGI HTTP Server for production
   - `whitenoise>=6.6.0` - Static file serving
   - `dj-database-url>=2.1.0` - Database URL parsing

### 2. **config/settings.py** - Updated for production:
   - Added `dj_database_url` and `os` imports
   - Added `WhiteNoiseMiddleware` for serving static files
   - Updated database configuration to support `DATABASE_URL` environment variable
   - Updated static files configuration with WhiteNoise (using `CompressedStaticFilesStorage` to avoid source map errors)
   - Changed `STATIC_URL` and `MEDIA_URL` to use leading slashes

### 3. **build.sh** - Created build script for Render:
   - Installs dependencies
   - Collects static files
   - Runs database migrations

### 4. **render.yaml** - Created Render configuration (optional, for Blueprint):
   - Defines PostgreSQL database
   - Defines web service configuration
   - Sets environment variables

### 5. **.env.example** - Updated with PostgreSQL and production examples

---

## Step-by-Step Deployment Instructions

### Step 1: Commit and Push Your Changes

Make sure all changes are committed and pushed to your GitHub repository on the `render` branch:

```bash
git add .
git commit -m "Configure app for Render deployment with PostgreSQL"
git push origin render
```

### Step 2: Create a Render Account

1. Go to https://render.com
2. Sign up for a free account
3. Connect your GitHub account

### Step 3: Create a PostgreSQL Database

1. From your Render dashboard, click **"New +"** and select **"PostgreSQL"**
2. Configure the database:
   - **Name**: `teamup-db` (or any name you prefer)
   - **Database**: `teamup` (or any name you prefer)
   - **User**: `teamup` (automatically generated)
   - **Region**: Choose the closest region to your users
   - **PostgreSQL Version**: 15 (or latest)
   - **Plan**: Free
3. Click **"Create Database"**
4. Wait for the database to be created (takes 1-2 minutes)
5. **IMPORTANT**: Copy the **Internal Database URL** - you'll need this later

### Step 4: Create a Web Service

1. From your Render dashboard, click **"New +"** and select **"Web Service"**
2. Connect your GitHub repository (authorize Render to access your repos)
3. Select your **TeamUp** repository
4. Configure the web service:

   **Basic Settings:**
   - **Name**: `teamup` (or any name you prefer)
   - **Region**: Same as your database
   - **Branch**: `render` (the branch you just pushed)
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`

   **Plan:**
   - Select **Free** tier

### Step 5: Configure Environment Variables

Still in the web service creation page, scroll to **"Environment Variables"** and add the following:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Or your preferred Python version |
| `SECRET_KEY` | (Click "Generate" or use your own) | Django secret key |
| `DEBUG` | `False` | **IMPORTANT**: Must be False in production |
| `DATABASE_URL` | (Paste Internal Database URL from Step 3) | PostgreSQL connection string |
| `GEMINI_API_KEY` | `your-gemini-api-key` | Your actual Gemini API key |

**Note:** You don't need to manually set `ALLOWED_HOSTS` - the app automatically detects the Render hostname using the `RENDER_EXTERNAL_HOSTNAME` environment variable that Render provides.

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will now:
   - Clone your repository
   - Install dependencies
   - Collect static files
   - Run migrations
   - **Create default admin account** (email: admin@teamup.com, password: password)
   - Start the gunicorn server

3. Monitor the deployment logs in real-time
4. Wait for the deployment to complete (first deployment takes 5-10 minutes)

### Step 7: Verify Deployment

1. Once deployment is complete, click the URL at the top of your service page
2. Your application should load successfully
3. Test the following:
   - Homepage loads correctly
   - Static files (CSS, JS, images) are working
   - User registration works
   - Login/logout functionality works

### Step 8: Access Admin Panel

A default admin account is automatically created during deployment:
- **Email:** admin@teamup.com
- **Password:** password

**⚠️ IMPORTANT SECURITY:** Change this password immediately after first login!

1. Go to: `https://your-app-name.onrender.com/admin/`
2. Login with the credentials above
3. Click on your username → Change password
4. Set a strong, unique password

**Alternative:** If you prefer to create your own admin account via Shell (paid plans only):

1. In your Render dashboard, go to your web service
2. Click on **"Shell"** in the left sidebar  
3. Run: `python manage.py createsuperuser`
4. Follow the prompts to create your admin account

---

## Post-Deployment Configuration

### Update ALLOWED_HOSTS if URL Changes

If you add a custom domain, you may need to update allowed hosts:

1. Go to your web service in Render
2. Navigate to **"Environment"** tab
3. Add or update the `ALLOWED_HOSTS` variable with your custom domain (comma-separated)
4. Click **"Save Changes"** - this will trigger a re-deployment

**Note:** The Render hostname is automatically included, so you only need to add custom domains.

### Set Up Custom Domain (Optional)

1. In your Render service, go to **"Settings"**
2. Scroll to **"Custom Domain"**
3. Add your domain
4. Follow the DNS configuration instructions provided by Render

### Enable Email (Optional)

To enable email functionality in production:

1. Update environment variables with your email provider settings:
   - `EMAIL_BACKEND` = `django.core.mail.backends.smtp.EmailBackend`
   - `EMAIL_HOST` = your SMTP host
   - `EMAIL_PORT` = SMTP port
   - `EMAIL_USE_TLS` = `True`
   - `EMAIL_HOST_USER` = your email
   - `EMAIL_HOST_PASSWORD` = your email password/app password

---

## Troubleshooting

### Static Files Not Loading

- Check that WhiteNoise is in MIDDLEWARE
- Verify `STATIC_ROOT` and `STATIC_URL` in settings
- Check build logs to ensure `collectstatic` ran successfully
- Try manual deployment: Shell → `python manage.py collectstatic --no-input`

### Database Connection Errors

- Verify `DATABASE_URL` is set correctly in environment variables
- Use the **Internal Database URL** (not external)
- Check database is running in Render dashboard
- Verify migrations ran: Shell → `python manage.py migrate`

### Application Crashes on Startup

- Check the logs in Render dashboard
- Verify all environment variables are set
- Make sure `DEBUG=False` in production
- Check that `SECRET_KEY` is set
- Verify `ALLOWED_HOSTS` includes your Render URL

### Import Errors

- Check that all dependencies are in `requirements.txt`
- Verify Python version matches your development environment
- Check build logs for installation errors

### Media Files Not Persisting

**Important**: Render's free tier uses ephemeral storage, meaning uploaded files (avatars, etc.) will be deleted when the service restarts.

**Solutions:**
1. **For production**: Use a cloud storage service like AWS S3, Cloudinary, or similar
2. **For testing**: Accept that uploads are temporary on free tier

To set up AWS S3 (recommended for production):
- Add `django-storages` and `boto3` to requirements.txt
- Configure S3 settings in settings.py
- Update environment variables with AWS credentials

---

## Maintenance

### Viewing Logs

- Go to your web service in Render dashboard
- Click **"Logs"** tab to see real-time application logs

### Manual Deployments

Render auto-deploys when you push to the connected branch. To manually deploy:
- Go to your web service
- Click **"Manual Deploy"** and select branch
- Click **"Deploy"**

### Running Management Commands

1. Go to your web service in Render
2. Click **"Shell"** in the sidebar
3. Run any Django management command:
   ```bash
   python manage.py <command>
   ```

### Backing Up Database

1. Go to your PostgreSQL database in Render
2. Click on the database name
3. Use the connection info to backup using `pg_dump`:
   ```bash
   pg_dump -h <host> -U <user> -d <database> > backup.sql
   ```

---

## Cost Considerations

**Free Tier Limitations:**
- Web services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-50 seconds
- PostgreSQL database limited to 90 days then deleted (backup regularly!)
- No persistent file storage

**Upgrading:**
- Paid plans start at $7/month for web services (no spin-down)
- PostgreSQL databases start at $7/month (persistent)

---

## Alternative Deployment Using render.yaml (Blueprint)

Instead of manual setup, you can use the included `render.yaml` file:

1. From Render dashboard, click **"New +"** → **"Blueprint"**
2. Connect your repository
3. Select the `render` branch
4. Render will read `render.yaml` and create both database and web service
5. You'll still need to manually set:
   - `ALLOWED_HOSTS` (with your Render URL)
   - `GEMINI_API_KEY` (your actual API key)

---

## Local Development After Changes

To continue developing locally with SQLite:

1. Your `.env` file should NOT have `DATABASE_URL` set
2. Either remove `DB_ENGINE` or set it to `django.db.backends.sqlite3`
3. Run migrations: `python manage.py migrate`
4. Your local app will use SQLite while production uses PostgreSQL

---

## Support

If you encounter issues:
1. Check Render's status page: https://status.render.com
2. Review Render's documentation: https://render.com/docs
3. Check application logs in Render dashboard
4. Review Django deployment checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

---

## Summary

You've successfully configured TeamUp for deployment on Render with:
- ✅ PostgreSQL database support
- ✅ Static file serving with WhiteNoise
- ✅ Production-ready WSGI server (Gunicorn)
- ✅ Environment-based configuration
- ✅ Automated build and deployment process

Your application is now ready for production! 🚀
