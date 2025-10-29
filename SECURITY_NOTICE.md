# 🔒 SECURITY NOTICE - Default Admin Credentials

## ⚠️ IMPORTANT: Change Default Password Immediately

Your TeamUp application automatically creates a default admin account during deployment for convenience on Render's free tier (which doesn't have shell access).

### Default Credentials

- **Email:** admin@teamup.com
- **Password:** password

### 🚨 CRITICAL: Change This Password Immediately!

**These credentials are publicly documented in your repository and deployment guides.**

### How to Change the Password

#### Option 1: Via Admin Panel (Recommended)

1. Go to: `https://your-app.onrender.com/admin/`
2. Login with the default credentials above
3. Click on your username in the top right
4. Select **"Change password"**
5. Enter a strong, unique password
6. Click **"Change my password"**

#### Option 2: Via Django Shell (if you have shell access)

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(email='admin@teamup.com')
admin.set_password('your-new-strong-password')
admin.save()
exit()
```

### Password Best Practices

✅ **DO:**
- Use at least 12 characters
- Mix uppercase, lowercase, numbers, and symbols
- Use a unique password (not used elsewhere)
- Consider using a password manager

❌ **DON'T:**
- Keep the default password "password"
- Use common words or patterns
- Share your admin credentials
- Write your password in plain text

### For Production Deployments

If deploying to production:

1. **Remove the default superuser creation** from `build.sh`:
   - Comment out or remove: `python manage.py create_default_superuser`

2. **Create a secure admin account manually** via shell access

3. **Use environment variables** for sensitive credentials:
   - Never hardcode passwords in your code
   - Use Render's environment variables feature

4. **Enable two-factor authentication** (if available in your Django setup)

5. **Regularly audit admin accounts** and remove unused ones

### Security Checklist

- [ ] Changed default admin password immediately after deployment
- [ ] Using a strong, unique password
- [ ] Not sharing admin credentials
- [ ] Regularly reviewing admin access logs
- [ ] For production: Removed automatic admin creation from build script

---

**Remember:** Security is your responsibility. The default admin account is provided for convenience on free tier deployments, but it's your job to secure it immediately.

🔐 Stay secure!
