# Common Deployment Issues and Fixes

## Issue: WhiteNoise "MissingFileError" for .map files

### Error Message:
```
whitenoise.storage.MissingFileError: The file 'assets/js/popper.min.js.map' could not be found
```

### Cause:
The `CompressedManifestStaticFilesStorage` backend tries to verify all referenced files in your JavaScript/CSS, including source map files (`.map`). Many third-party libraries reference these files, but they may not be included in your static files.

### Solution:
Changed the `STATICFILES_STORAGE` setting in `config/settings.py` from:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

To:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

### Trade-offs:
- **CompressedManifestStaticFilesStorage**: Stricter validation, better for cache busting, but requires all referenced files
- **CompressedStaticFilesStorage**: More forgiving, still provides compression, but less aggressive cache busting

For most Django applications, `CompressedStaticFilesStorage` is sufficient and avoids these common issues.

### Status:
✅ **FIXED** - This change has been applied to your codebase and pushed to the `render` branch.

---

## Other Common Issues

### Issue: Database Connection Errors

**Symptom:** Application crashes with database connection errors

**Solutions:**
1. Verify `DATABASE_URL` environment variable is set correctly
2. Use the **Internal Database URL** (not external) from Render
3. Check that the PostgreSQL database is running in Render dashboard
4. Ensure migrations completed during build

### Issue: Static Files Not Loading

**Symptom:** CSS/JS files return 404 or page looks unstyled

**Solutions:**
1. Check that `WhiteNoiseMiddleware` is in MIDDLEWARE list
2. Verify `collectstatic` ran successfully in build logs
3. Check `STATIC_ROOT` and `STATIC_URL` settings
4. Try running `python manage.py collectstatic --no-input` in Render Shell

### Issue: Application Not Starting

**Symptom:** "Application failed to start" or immediate crash

**Solutions:**
1. Check logs in Render dashboard for specific error
2. Verify all required environment variables are set
3. Ensure `DEBUG=False` in production
4. Check that `SECRET_KEY` is set and not empty
5. Verify `ALLOWED_HOSTS` includes your Render URL

### Issue: Import Errors

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solutions:**
1. Verify all dependencies are in `requirements.txt`
2. Check Python version in `runtime.txt` matches your development
3. Review build logs for package installation errors
4. Ensure `requirements.txt` has no typos

### Issue: Media Files Disappear

**Symptom:** Uploaded files (avatars, images) are lost after restart

**Explanation:** Render's free tier uses ephemeral storage - files uploaded to the filesystem are deleted on restart.

**Solutions:**
1. **For production:** Use cloud storage (AWS S3, Cloudinary, etc.)
2. **For testing:** Accept temporary storage on free tier
3. Consider upgrading to paid plan with persistent disk

---

## Getting Help

If you encounter other issues:

1. **Check Render Logs:** Most errors show up here with stack traces
2. **Review Build Logs:** See if dependencies installed correctly
3. **Test Locally:** Run the same commands from `build.sh` locally
4. **Render Status:** Check https://status.render.com for platform issues
5. **Django Deployment Checklist:** https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

---

## Testing Locally Before Deploy

Run these commands to catch issues before deploying:

```bash
# Test static file collection
python manage.py collectstatic --no-input

# Check for migrations
python manage.py makemigrations --check --dry-run

# Run migrations
python manage.py migrate

# Check deployment readiness
python manage.py check --deploy
```

---

Last updated: After fixing WhiteNoise storage backend issue
