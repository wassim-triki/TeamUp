@echo off
REM Migration Setup Script for TeamUp Signup Wizard
REM This script helps set up the MySQL database for the new custom User model

echo ======================================
echo TeamUp - Database Migration Setup
echo ======================================
echo.

echo WARNING: This will reset your MySQL database!
echo.
echo Current database: teamup_db
echo MySQL User: root
echo.
echo This script will:
echo   1. Drop the existing database
echo   2. Create a fresh database
echo   3. Run all migrations
echo.
set /p answer="Do you want to continue? (yes/no): "

if /i "%answer%"=="yes" (
    echo.
    echo Dropping and recreating MySQL database...
    mysql -u root -p -e "DROP DATABASE IF EXISTS teamup_db; CREATE DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to recreate database. Make sure MySQL is running and password is correct.
        pause
        exit /b 1
    )
    
    echo Database recreated successfully!
    
    echo.
    echo Removing old migration files...
    for /r apps %%i in (migrations\*.py) do (
        if not "%%~nxi"=="__init__.py" del "%%i"
    )
    for /r apps %%i in (migrations\*.pyc) do del "%%i"
    echo Old migrations removed
) else (
    echo.
    echo Cancelled. Please handle migrations manually.
    exit /b 1
)

echo.
echo Creating migrations for users app...
python manage.py makemigrations users

echo.
echo Creating migrations for all apps...
python manage.py makemigrations

echo.
echo Running migrations...
python manage.py migrate

echo.
echo Migration setup complete!
echo.
echo Next steps:
echo 1. Create a superuser: python manage.py createsuperuser
echo 2. Run the server: python manage.py runserver
echo 3. Test signup at: http://localhost:8000/users/signup/
echo.
echo ======================================
pause
