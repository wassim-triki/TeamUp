# Pre-Deployment Checklist for Render

## Before Pushing to GitHub

- [ ] All changes committed to the `render` branch
- [ ] `.env` file is NOT committed (should be in .gitignore)
- [ ] `requirements.txt` includes all production dependencies
- [ ] `build.sh` script is present
- [ ] `runtime.txt` specifies Python version
- [ ] Test locally that migrations work: `python manage.py migrate`
- [ ] Test locally that static files collect: `python manage.py collectstatic`

## Files to Verify

- [ ] `config/settings.py` - Database and static files configured
- [ ] `requirements.txt` - Contains psycopg2-binary, gunicorn, whitenoise, dj-database-url
- [ ] `build.sh` - Build script for Render
- [ ] `render.yaml` - Optional blueprint configuration
- [ ] `runtime.txt` - Python version specification
- [ ] `.gitignore` - Contains .env and sensitive files

## Information You'll Need

- [ ] Gemini API Key: `_____________________________`
- [ ] GitHub repository URL: `_____________________________`
- [ ] Render account created: Yes / No
- [ ] Desired app name: `_____________________________`

## Deployment Steps

1. [ ] Push code to GitHub `render` branch
2. [ ] Create PostgreSQL database on Render
3. [ ] Save Internal Database URL
4. [ ] Create Web Service on Render
5. [ ] Configure environment variables:
   - [ ] PYTHON_VERSION
   - [ ] SECRET_KEY (generate new)
   - [ ] DEBUG = False
   - [ ] ALLOWED_HOSTS = your-app.onrender.com
   - [ ] DATABASE_URL (from step 3)
   - [ ] GEMINI_API_KEY
6. [ ] Deploy and monitor logs
7. [ ] Test application URL
8. [ ] Create superuser via Shell
9. [ ] Test admin panel

## Post-Deployment

- [ ] Application loads correctly
- [ ] Static files working (CSS, JS, images)
- [ ] User registration works
- [ ] Login/logout works
- [ ] Database queries work
- [ ] Admin panel accessible
- [ ] No errors in logs

## Notes

- First deployment takes 5-10 minutes
- Free tier spins down after 15 min inactivity
- First request after spin-down takes 30-50 seconds
- Uploaded files are ephemeral on free tier
- PostgreSQL free tier expires after 90 days

---

Good luck with your deployment! 🚀
