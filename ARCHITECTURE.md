TeamUp — Architecture (Medium layout)
===================================

Overview
--------
This repo uses a compact, collaborator-friendly "Medium" layout with three main local apps:

- apps/core — public site (landing pages) and the dashboard UI. Templates live under `templates/core/`.
- apps/users — authentication, profiles, and user-related business logic. Templates live under `templates/users/`.
- apps/api  — JSON / REST endpoints. (Consider DRF later.)

Why this layout
----------------
- Low cognitive overhead for new contributors: only three local apps to learn.
- Logical separation: UI (core), user domain (users), and API surface (api).
- Easy to split further later if features grow.

Developer notes
---------------
- URLs:
  - Root include in `config/urls.py` points to `apps.core.urls` for the public site.
  - `accounts/` routes point to `apps.users.urls` (namespace `users`).
  - `api/` routes point to `apps.api.urls` (namespace `api`).

- Templates should be namespaced under `templates/<app_label>/...` so it's clear where to find them.
- Add tests under `apps/<app>/tests/` to keep tests close to code ownership.

Migration / refactor notes
-------------------------
- Dashboard app was merged into `apps.core`. If you need to split later, move dashboard views into `apps/dashboard` and add it to `INSTALLED_APPS`.
- The previous `apps.accounts` and `apps.dashboard` folders are kept as compatibility stubs to avoid breaking local branches; use `apps.users` and `apps.core` going forward.

Next steps
----------
- Add `.env.sample` describing environment variables (SECRET_KEY, DEBUG, DB_*).
- Add a short CONTRIBUTING.md and a minimal test to demonstrate the test pattern.
# TeamUp — Project architecture

This document explains the base folder structure created to help collaborators get started.

Top-level layout
- `manage.py` — Django CLI
- `config/` — Django project settings, urls, wsgi/asgi
- `apps/` — local Django apps (core, accounts, dashboard, api)
- `templates/` — shared templates (project-level `base.html` exists)
- `static/` — shared static assets

Apps created (skeletons)
- `apps.core` — public-facing routes and landing pages. Template: `core/index.html`.
- `apps.accounts` — authentication-related pages (login), template: `accounts/login.html`.
- `apps.dashboard` — admin/user dashboard UI skeleton.
- `apps.api` — JSON endpoints and future REST API.

Routing
- Root `config/urls.py` includes:
  - `/` -> `apps.core`
  - `/accounts/` -> `apps.accounts`
  - `/dashboard/` -> `apps.dashboard`
  - `/api/` -> `apps.api`

How to extend
- Add views, templates, and models inside each `apps.<app>` package.
- Register models in the app's `admin.py`.
- Add app-specific static files to `static/` or `apps/<app>/static/`.

Next steps
- Implement authentication, permissions, and real dashboard pages.
- Add tests for each app (unit + integration).
