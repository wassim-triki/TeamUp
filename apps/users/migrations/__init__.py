# Generated migration file template
# Run: python manage.py makemigrations users
# Then: python manage.py migrate

"""
This directory will contain Django migrations for the users app.

To create migrations for the new models:
1. Run: python manage.py makemigrations users
2. Review the generated migration file
3. Run: python manage.py migrate

Note: Since we're using a custom User model (AUTH_USER_MODEL = 'users.User'),
you may need to delete the existing database (db.sqlite3) and start fresh
if you've already run migrations with the default Django User model.

Steps to reset database (development only):
1. Delete db.sqlite3
2. Delete all migration files in apps/users/migrations/ except __init__.py
3. Run: python manage.py makemigrations users
4. Run: python manage.py migrate
5. Run: python manage.py createsuperuser
"""
