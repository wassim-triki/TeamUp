# TeamUp — Architecture (brief)

## Overview

This repository uses a compact, collaborator-friendly "Medium" layout with three local apps:

- apps/core — public site (landing pages) + dashboard UI. Templates: `templates/core/`.
- apps/users — authentication, profiles, and user-related logic. Templates: `templates/users/`.
- apps/api — JSON / REST endpoints (ready for DRF later).

## Why this layout

- Low cognitive overhead for new contributors: three local apps to learn.
- Clear ownership: UI (core), users, and API.

## Notes

- URLs: `config/urls.py` includes `apps.core`, `apps.users` (mounted at `/accounts/`), and `apps.api` (at `/api/`).
- Templates are namespaced under `templates/<app_label>/`.
- Tests should live under `apps/<app>/tests/`.

If you need to expand, split an app into a focused app (e.g., move dashboard to `apps/dashboard`).

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
