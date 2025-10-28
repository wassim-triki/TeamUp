# 🐬 MySQL Database Setup for Signup Wizard

## ✅ Your Current Configuration

Based on your `.env` file, you're using:

- **Database**: MySQL
- **Database Name**: `teamup_db`
- **User**: `root`
- **Password**: `140111`
- **Host**: `localhost`
- **Port**: `3306`

This is **already configured correctly** in `config/settings.py`! ✓

## 🚀 Migration Steps for MySQL

Since we're adding a custom User model, you need to reset your database:

### Option 1: Using the Script (Recommended)

```bash
# Windows
setup_migrations.bat

# Linux/Mac
bash setup_migrations.sh
```

This will:

1. Drop the existing `teamup_db` database
2. Create a fresh `teamup_db` database
3. Remove old migration files
4. Create new migrations
5. Run all migrations

### Option 2: Manual Setup

**Step 1: Reset MySQL Database**

Open MySQL command line or MySQL Workbench:

```sql
-- Connect to MySQL
mysql -u root -p
-- Enter password: 140111

-- Drop and recreate database
DROP DATABASE IF EXISTS teamup_db;
CREATE DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Verify database exists
SHOW DATABASES;

-- Exit MySQL
exit
```

**Step 2: Remove Old Migrations**

```bash
# Windows
del /S apps\users\migrations\*.py
# Make sure to keep __init__.py

# Linux/Mac
find apps/*/migrations -name "*.py" ! -name "__init__.py" -delete
```

**Step 3: Create and Run Migrations**

```bash
# Create migrations for users app (custom User model)
python manage.py makemigrations users

# Create migrations for all apps
python manage.py makemigrations

# Apply all migrations
python manage.py migrate

# Verify tables created
python manage.py dbshell
# Then in MySQL: SHOW TABLES;
```

**Step 4: Create Superuser**

```bash
python manage.py createsuperuser
# Email: admin@teamup.com
# Username: admin (auto-generated from email)
# Password: (choose strong password)
```

**Step 5: Run Server**

```bash
python manage.py runserver
```

## 🔍 Verify Database Tables

After migration, these tables should exist in MySQL:

```sql
-- Connect to database
mysql -u root -p teamup_db

-- List all tables
SHOW TABLES;

-- Should see:
-- users_user
-- users_userprofile
-- users_emailverificationtoken
-- django_migrations
-- django_session
-- auth_* tables
-- etc.

-- Check user table structure
DESCRIBE users_user;

-- Exit
exit
```

## 🐛 Common MySQL Issues

### Issue 1: "Access denied for user 'root'"

**Solution:** Check password in `.env` file matches your MySQL root password

```bash
# Test MySQL connection
mysql -u root -p
# Enter password: 140111
```

### Issue 2: "Unknown database 'teamup_db'"

**Solution:** Database doesn't exist, create it:

```sql
mysql -u root -p
CREATE DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
```

### Issue 3: "Can't connect to MySQL server"

**Solution:** Make sure MySQL is running

```bash
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql

# Mac
brew services start mysql
```

### Issue 4: Character encoding issues

**Solution:** Ensure database uses utf8mb4

```sql
ALTER DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue 5: Migration conflicts

**Solution:** Reset migrations

```bash
# Delete migration files
del /S apps\users\migrations\*.py

# Drop and recreate database
mysql -u root -p -e "DROP DATABASE teamup_db; CREATE DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run fresh migrations
python manage.py makemigrations users
python manage.py migrate
```

## 📊 MySQL Workbench Setup

If you prefer GUI:

1. Open MySQL Workbench
2. Connect to localhost (root/140111)
3. Right-click "Schemas" → "Create Schema"
4. Name: `teamup_db`
5. Charset: `utf8mb4`
6. Collation: `utf8mb4_unicode_ci`
7. Apply

Then run migrations from terminal.

## 🔐 Security Note

Your `.env` file contains:

```env
DB_PASSWORD=140111
```

For production:

- Use a stronger password
- Don't commit `.env` to git
- Use environment variables on server

## ✅ Verification Checklist

After setup, verify:

- [ ] MySQL is running
- [ ] Database `teamup_db` exists
- [ ] Table `users_user` exists
- [ ] Table `users_userprofile` exists
- [ ] Table `users_emailverificationtoken` exists
- [ ] Can access Django admin
- [ ] Can create test user via signup
- [ ] Verification email works

## 🎯 Quick Test

```bash
# 1. Check database
mysql -u root -p teamup_db -e "SHOW TABLES;"

# 2. Check Django connection
python manage.py dbshell
# Should open MySQL prompt

# 3. Run Django checks
python manage.py check

# 4. Start server
python manage.py runserver

# 5. Visit signup
# http://localhost:8000/users/signup/
```

## 📚 MySQL Resources

- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Django MySQL Notes](https://docs.djangoproject.com/en/4.2/ref/databases/#mysql-notes)
- [Character Set](https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-utf8mb4.html)

---

**Your MySQL configuration is correct!** Just need to run the migrations. 🚀
