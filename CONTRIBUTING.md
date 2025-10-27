# Contributing to TeamUp

Thanks for helping — this file keeps things simple. It covers how to run the project and where to add code.

1. Minimum setup (local dev)

- Create & activate a virtual environment:

  ```bash
  python -m venv .venv
  source .venv/Scripts/activate   # Git Bash / bash.exe on Windows
  ```

- Install dependencies:

  ```bash
  pip install -r requirements.txt
  pip install python-decouple
  ```

- Copy the example env and edit (`.env`):

  ```bash
  cp .env.example .env
  ```

- Run migrations and start the dev server:

  ```bash
  python manage.py migrate
  python manage.py runserver
  ```

2. Branch naming

- Use: `your-name/your-feature-name` (for example `wassim/add-login-page`). Keep branch names short and descriptive.

3. Where to add things (apps folder)

This project uses a small set of apps. Add code in the app that best matches the feature's domain.

- `apps/core` — Public site and dashboard UI

  - Put landing pages, site-wide templates, and dashboard views here.
  - Templates: `templates/core/`.

- `apps/users` — Authentication and user profiles

  - Add auth views, profile models, and user-related business logic here.
  - Templates: `templates/users/`.

- `apps/api` — JSON / REST endpoints
  - Add API views, serializers (when using DRF), and endpoint routing here.

Notes

- Keep code and templates namespaced (`templates/<app_label>/...`) so it's easy for contributors to find things.
- If a feature spans multiple domains, prefer creating a small module in the most relevant app rather than adding unrelated code across apps.
