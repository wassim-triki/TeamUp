# TeamUp

TeamUp is a web platform that helps people find compatible sports partners or groups based on interests, skill level, and availability. The platform will use AI for smarter partner recommendations and intelligent scheduling suggestions.

Repository: https://github.com/KamilChakroun/TeamUp.git

This repository was scaffolded from a previous project. The README and settings have been updated to provide a minimal, local-first development setup.

## Quick local setup (development)

These steps will get the project running locally using a Python virtual environment and SQLite (no external DB required).

Requirements

- Python 3.8+
- Git

1. Clone

```bash
git clone https://github.com/KamilChakroun/TeamUp.git
cd TeamUp
```

2. Create and activate virtualenv

```bash
python -m venv venv
# If you're using Git Bash (bash.exe):
source venv/Scripts/activate
# For Windows CMD use: venv\Scripts\activate
# For PowerShell: venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment

Copy the example env and edit if needed:

```bash
cp .env.example .env
# On Windows PowerShell: copy-item .env.example .env
```

.env defaults to SQLite for local development. If you prefer MySQL/Postgres, update DB*ENGINE and DB*\* variables accordingly.

5. Run migrations and create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

## Development admin account (local)

For convenience the following development admin account can be used to sign into the Django admin on a local development instance. This account is intended for local/dev only — do NOT use these credentials in production.

- Username: admin
- Email: admin@teamup.com
- Password: admin123

If you prefer, create your own admin user with:

```bash
python manage.py createsuperuser
```

## Notes on running commands: Git Bash (bash.exe) vs Windows CMD vs PowerShell

Some commands differ slightly depending on the shell your teammates use. Below are the recommended equivalents so everyone on the team can follow the same setup.

1. Create and activate virtual environment

# Git Bash (bash.exe)

```bash
python -m venv venv
source venv/Scripts/activate
```

# Windows CMD

```cmd
python -m venv venv
venv\Scripts\activate
```

# PowerShell

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy the example env file

# Git Bash / bash.exe:

```bash
cp .env.example .env
```

# Windows CMD:

```cmd
copy .env.example .env
```

# PowerShell:

```powershell
Copy-Item .env.example .env
```

4. Migrate and runserver (same across shells)

```bash
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser and log into the admin at http://127.0.0.1:8000/admin/ using the dev admin credentials above (or your own created superuser).

If you'd like, I can also add a short CONTRIBUTING.md or a developer quickstart script (PowerShell + bash variants) to make onboarding even easier for teammates — tell me which you'd prefer.
