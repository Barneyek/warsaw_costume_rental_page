# Plan: [GH-1] Initialize Django project structure with split settings

**Issue:** https://github.com/Barneyek/warsaw_costume_rental_page/issues/1
**Status:** 🟢 Done
**Created:** 2026-04-23
**Last updated:** 2026-04-23
**Estimated effort:** M (1-4h)
**Actual effort:** M (~2h implementation + validation)

---

## 1. Context & Goal

This issue establishes the foundational Django project skeleton on which every subsequent issue (models, API, admin, i18n, frontend) depends. The scope is deliberately narrow: settings, environment, app registration, third-party middleware wiring, and the OpenAPI schema endpoint that will serve as the contract for the frontend type-generation pipeline.

**Architectural context (authoritative — see `docs/lessons-learned.md`):**

- `drf-spectacular` is the project's OpenAPI layer. It auto-generates `schema.yaml` from DRF serializers.
- In issue #14, `orval` will consume `GET /api/schema/` to generate TanStack Query hooks + Zod schemas on the frontend. **This endpoint must exist and return a valid, warning-free schema by the time issue #1 closes.**
- The previous "No OpenAPI" decision has been superseded. `drf_spectacular` is intentional architecture, not debt.
- Zod schemas for API responses are NEVER written by hand — they come from orval. (Form-only validation is the only exception.)

**State at plan creation (2026-04-23):**

The initial commit (959a111) scaffolded ~75% of the structure. This plan closes the remaining gaps.

| Item | File | Status |
|------|------|--------|
| Project layout (`backend/web_app/`) | — | ✅ Done |
| All 5 apps in `backend/src/` | — | ✅ Done |
| Split settings (`base.py`, `dev.py`, `test.py`) | — | ✅ Done |
| `INSTALLED_APPS` with `src.X` dotted paths | `base.py` | ✅ Done |
| `drf_spectacular` in `INSTALLED_APPS` | `base.py` | ✅ Done |
| `REST_FRAMEWORK.DEFAULT_SCHEMA_CLASS` set | `base.py` | ✅ Done |
| OpenAPI URLs (`/api/schema/`, `/api/docs/`, `/api/redoc/`) | `urls.py` | ✅ Done |
| CORS middleware first in `MIDDLEWARE` | `base.py` | ✅ Done |
| `MEDIA_ROOT` / `MEDIA_URL` configured | `base.py` | ✅ Done |
| `pytest.ini` pointing at `test.py` settings | `pytest.ini` | ✅ Done |
| `drf-spectacular` in `requirements.txt` | `requirements.txt` | ✅ Done |
| `django-modeltranslation` in `requirements.txt` | `requirements.txt` | ✅ Done |
| `.env` in `.gitignore` / `!.env.example` | `.gitignore` | ✅ Done |
| `DJANGO_SETTINGS_MODULE` default in `manage.py` | `manage.py` | ✅ Done |
| `.env.example` committed | project root | ❌ **Missing** |
| `SECRET_KEY` loaded from env | `base.py` | ❌ **Missing** (hardcoded) |
| `python-dotenv` wired via `load_dotenv()` | `manage.py` | ❌ **Missing** (installed, not called) |
| `modeltranslation` in `INSTALLED_APPS` before `admin` | `base.py` | ❌ **Missing** entirely |
| `LANGUAGES` + `MODELTRANSLATION_*` settings | `base.py` | ❌ **Missing** |
| `LANGUAGE_CODE` = `'pl'` (not `'pl-pl'`) | `base.py` | ❌ **Wrong** (mismatch with `LANGUAGES` entries) |
| `SPECTACULAR_SETTINGS.COMPONENT_SPLIT_REQUEST` | `base.py` | ❌ **Missing** (required for orval) |
| `CORS_ALLOWED_ORIGINS` scoped to port 5173 | `dev.py` | ❌ **Wrong** (`CORS_ALLOW_ALL_ORIGINS = True`) |
| DB vars from env (no hardcoded defaults) | `dev.py` | ❌ **Weak** (has fallback defaults in `os.environ.get()`) |
| Smoke tests (settings, `/api/schema/`, `/api/docs/`) | `tests/` | ❌ **Missing** |

**Why this matters:** Without `modeltranslation` in `INSTALLED_APPS`, future `makemigrations` silently omits translated columns. Without `COMPONENT_SPLIT_REQUEST`, orval generates malformed types for mutation endpoints. Without `load_dotenv()`, `.env` is never read locally — every developer runs blind unless inside Docker.

---

## 2. Scope

### In scope
- [ ] Create `.env.example` with all required variables documented
- [ ] Add `load_dotenv()` to `manage.py` so `.env` is read in local dev (without Docker)
- [ ] Move `SECRET_KEY` from hardcoded string → `os.environ['SECRET_KEY']` (fail loud)
- [ ] Add `DB_HOST` to `.env` and `.env.example`
- [ ] Add `modeltranslation` to `INSTALLED_APPS` before `django.contrib.admin`
- [ ] Add `LANGUAGES`, `MODELTRANSLATION_DEFAULT_LANGUAGE`, `MODELTRANSLATION_FALLBACK_LANGUAGES` to `base.py`
- [ ] Fix `LANGUAGE_CODE` from `'pl-pl'` → `'pl'` (must match `LANGUAGES` codes exactly)
- [ ] Add `COMPONENT_SPLIT_REQUEST: True` and `SERVE_INCLUDE_SCHEMA: False` to `SPECTACULAR_SETTINGS`
- [ ] Replace `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOWED_ORIGINS` scoped to port 5173
- [ ] Remove fallback defaults from `os.environ.get()` calls in `dev.py`
- [ ] Write pytest smoke tests: settings integrity, `/api/schema/` returns 200, `/api/docs/` returns 200
- [ ] Validate `python manage.py spectacular --file schema.yaml` runs with zero warnings

### Out of scope (świadomie pomijamy)
- Django models (issues #4-#8) — *powód:* each app gets its own issue with model definition, migration, and admin
- API endpoints beyond `/api/schema/` and `/api/docs/` (issues #9-#13) — *powód:* no business logic yet
- Frontend: orval config, TanStack Query setup, Zod generation (issue #14) — *powód:* frontend depends on the schema endpoint this issue creates, not the other way around
- Docker Compose improvements (issue #3) — *powód:* out of scope per issue list
- Production settings (`settings/prod.py`) — *powód:* no deployment target defined yet
- `modeltranslation` `translation.py` files per app — *powód:* done alongside each model issue

---

## 3. Affected files & modules

| Path | Action | Why |
|------|--------|-----|
| `.env.example` | **NEW** | Acceptance criterion; onboarding contract for any dev |
| `.env` | **MODIFY** | Add `SECRET_KEY` and `DB_HOST` keys (already exists with DB_NAME/USER/PASS) |
| `backend/manage.py` | **MODIFY** | Add `load_dotenv()` call before Django touches env |
| `backend/web_app/settings/base.py` | **MODIFY** | SECRET_KEY from env; add modeltranslation; LANGUAGES; fix LANGUAGE_CODE; SPECTACULAR_SETTINGS |
| `backend/web_app/settings/dev.py` | **MODIFY** | CORS scoped to 5173; remove fallback defaults from DB env vars |
| `backend/tests/test_settings_smoke.py` | **NEW** | Pytest smoke tests for settings + schema endpoints |

---

## 4. Pre-conditions / Dependencies

**Musi być gotowe wcześniej:**
- [x] Python virtual environment activated with all packages from `requirements.txt` installed
- [x] Docker Desktop running (PostgreSQL needed for dev validation steps 5.9.2–5.9.4)
- [x] `.env` file exists at project root (already has `DB_NAME`, `DB_USER`, `DB_PASS`)
- [x] Initial commit 959a111 present (scaffold in place)
- [x] `drf-spectacular` installed: `pip show drf-spectacular` shows a version

**Verify before starting:**
```bash
# From project root, in venv:
pip show django djangorestframework django-cors-headers drf-spectacular \
    django-modeltranslation django-filter Pillow django-imagekit python-dotenv \
    pytest pytest-django
```
All must print a `Version:` line. If any show `not found` — run `pip install -r backend/requirements.txt` first.

**Jeśli coś z powyższego nie jest gotowe — STOP, nie zaczynaj.**

---

## 5. Implementation steps

> Krok uznajemy za ukończony TYLKO gdy `validate` zwraca `expected`.
> Każdy krok wykonaj w kolejności — kroki 5.2 i 5.5 zależą od 5.1.

---

### 5.1 Wire `load_dotenv()` in `manage.py`

#### Step 5.1.1: Add `load_dotenv()` call at the top of `manage.py`

- [x] **Action:** Edit `backend/manage.py`. Add `from pathlib import Path` and `from dotenv import load_dotenv` at the top. Call `load_dotenv()` with an explicit path **before** the `main()` function — it must run before any Django import touches `os.environ`.

  Final `backend/manage.py`:
  ```python
  #!/usr/bin/env python
  """Django's command-line utility for administrative tasks."""
  import os
  import sys
  from pathlib import Path

  from dotenv import load_dotenv

  load_dotenv(Path(__file__).resolve().parent.parent / '.env')


  def main():
      """Run administrative tasks."""
      os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_app.settings.dev')
      try:
          from django.core.management import execute_from_command_line
      except ImportError as exc:
          raise ImportError(
              "Couldn't import Django. Are you sure it's installed and "
              "available on your PYTHONPATH environment variable? Did you "
              "forget to activate a virtual environment?"
          ) from exc
      execute_from_command_line(sys.argv)


  if __name__ == '__main__':
      main()
  ```

  **Path resolution:** `Path(__file__).resolve().parent` = `d:\Praca\warsaw_costume_rental\backend`. `.parent` = `d:\Praca\warsaw_costume_rental`. `/ '.env'` = `d:\Praca\warsaw_costume_rental\.env`. ✅ Correct.

  **Docker compatibility:** Inside Docker, `docker-compose.yml` injects env vars directly via the `environment:` block (reading from the host `.env`). `load_dotenv()` with `override=False` (the default) does NOT overwrite already-set env vars — so Docker-injected vars remain authoritative and the call is a safe no-op in that context.

- [x] **Validate:** From `backend/` (venv active, NOT via Docker), run:
  ```bash
  python -c "
  from pathlib import Path
  from dotenv import load_dotenv
  import os
  load_dotenv(Path('manage.py').resolve().parent.parent / '.env')
  print(os.environ.get('DB_NAME', 'NOT LOADED'))
  "
  ```
- [x] **Expected:** Prints `django_db` (or whatever `DB_NAME` is in your `.env`), NOT `NOT LOADED`.
- [x] **On failure:** (a) Confirm `.env` exists at project root: `ls d:/Praca/warsaw_costume_rental/.env`. (b) Confirm `python-dotenv` is installed: `pip show python-dotenv`. (c) Double-check path calculation by printing `Path('manage.py').resolve().parent.parent`.

---

### 5.2 Move `SECRET_KEY` to environment

#### Step 5.2.1: Add `SECRET_KEY` (and `DB_HOST`) to the real `.env`

- [x] **Action:** Edit `d:\Praca\warsaw_costume_rental\.env`. Add two keys so the file becomes:
  ```dotenv
  DB_NAME=django_db
  DB_USER=admin
  DB_PASS=admin
  DB_HOST=db
  SECRET_KEY=django-insecure-d67553cq8)p5vc#1#9*_b_n2i+ye)9_no%@*_*6%e%u#tr(4d(
  ```
  (`DB_HOST=db` matches the Docker service name. When running `manage.py` locally without Docker, this value is unused — the DB call fails on connection, not on missing env var.)

- [x] **Validate:** `grep -c "SECRET_KEY" d:/Praca/warsaw_costume_rental/.env`
- [x] **Expected:** `1`
- [x] **On failure:** Open `.env` in editor and add the line manually. Ensure no trailing spaces or quotes around the value.

#### Step 5.2.2: Update `base.py` to load `SECRET_KEY` from env

- [x] **Action:** Edit `backend/web_app/settings/base.py`:
  1. Add `import os` at the top (currently missing).
  2. Replace the hardcoded `SECRET_KEY` line with `os.environ['SECRET_KEY']`.

  Lines to change (currently at lines 1 and 5):
  ```python
  # Before:
  from pathlib import Path

  BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

  SECRET_KEY = 'django-insecure-d67553cq8)p5vc#1#9*_b_n2i+ye)9_no%@*_*6%e%u#tr(4d('

  # After:
  import os
  from pathlib import Path

  BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

  SECRET_KEY = os.environ['SECRET_KEY']
  ```

  **Why `os.environ['SECRET_KEY']` and not `.get('SECRET_KEY')`:** Using `[]` raises `KeyError` immediately at startup if the key is missing. This surfaces the configuration error early with a clear message. A silent `None` or fallback default would let Django start in a broken state.

- [x] **Validate:** From `backend/` (venv active), run:
  ```bash
  python -c "
  import os, sys
  sys.path.insert(0, '.')
  from pathlib import Path
  from dotenv import load_dotenv
  load_dotenv(Path('.').resolve().parent / '.env')
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_app.settings.dev')
  import django
  django.setup()
  from django.conf import settings
  print(settings.SECRET_KEY[:30])
  "
  ```
- [x] **Expected:** Prints the first 30 characters of the key: `django-insecure-d67553cq8)p5v`
- [x] **On failure:** Confirm Step 5.1.1 is complete (dotenv loads before Django). Confirm `.env` has `SECRET_KEY=...` (Step 5.2.1). If you see `KeyError: 'SECRET_KEY'` — dotenv is not loading the file; debug the path.

---

### 5.3 Create `.env.example`

#### Step 5.3.1: Create `.env.example` at project root

- [x] **Action:** Create `d:\Praca\warsaw_costume_rental\.env.example` with the following content:
  ```dotenv
  # ================================================
  # Warsaw Costume Rental — environment template
  # Copy this file to .env and fill in your values.
  # NEVER commit the real .env file.
  # ================================================

  # Database (PostgreSQL — matches Docker service name)
  DB_NAME=django_db
  DB_USER=admin
  DB_PASS=admin
  DB_HOST=db

  # Django secret key — generate your own:
  # python -c "from django.core.signing import get_random_string; print(get_random_string(50))"
  SECRET_KEY=your-secret-key-here
  ```

- [x] **Validate:** `cat d:/Praca/warsaw_costume_rental/.env.example`
- [x] **Expected:** File exists and contains all 5 keys: `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `SECRET_KEY`.
- [x] **On failure:** Create the file manually. Ensure the filename is exactly `.env.example` (no `.txt` suffix, leading dot required).

#### Step 5.3.2: Verify `.gitignore` rules are correct

- [x] **Action:** Read `.gitignore` and confirm the two required lines exist.
- [x] **Validate:**
  ```bash
  grep -n "\.env" d:/Praca/warsaw_costume_rental/.gitignore
  ```
- [x] **Expected:** Output contains:
  ```
  47:.env
  52:!.env.example
  ```
  (Line numbers may vary.) The `.env` line ignores the real secrets file. The `!.env.example` line un-ignores the template so it IS committed. Both must be present.
- [x] **On failure:** If `.env` line is missing — add it under the Environment & secrets section. If `!.env.example` is missing — add it on the next line after `.env`.

---

### 5.4 Fix `INSTALLED_APPS` — add `modeltranslation` before `admin`

#### Step 5.4.1: Insert `modeltranslation` at position [0] in `INSTALLED_APPS`

- [x] **Action:** Edit `backend/web_app/settings/base.py`. Restructure `INSTALLED_APPS` to:
  ```python
  INSTALLED_APPS = [
      'modeltranslation',             # MUST be before django.contrib.admin
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      # Third party
      'rest_framework',
      'corsheaders',
      'django_filters',
      'drf_spectacular',
      # Local
      'src.core',
      'src.catalogue',
      'src.blog',
      'src.pages',
      'src.inquiry',
  ]
  ```

  **Why `modeltranslation` must be first:** `django-modeltranslation` monkey-patches `django.contrib.admin` to add translation tabs to ModelAdmin forms. If `admin` is imported before `modeltranslation`, the patch never applies and the admin UI will show only the base (untranslated) fields even after `translation.py` files are added. This is a silent failure — everything appears to work but translation fields are absent from the admin interface.

- [x] **Validate:**
  ```bash
  cd backend && python manage.py shell -c "
  from django.conf import settings
  apps = list(settings.INSTALLED_APPS)
  print('modeltranslation index:', apps.index('modeltranslation'))
  print('admin index:', apps.index('django.contrib.admin'))
  print('OK' if apps.index('modeltranslation') < apps.index('django.contrib.admin') else 'FAIL — wrong order')
  "
  ```
- [x] **Expected:**
  ```
  modeltranslation index: 0
  admin index: 1
  OK
  ```
- [x] **On failure:** Check that you edited `base.py` (not `dev.py`). Confirm `modeltranslation` is the very first entry in the list.

#### Step 5.4.2: Verify all 5 local apps are registered

- [x] **Action:**
  ```bash
  cd backend && python manage.py shell -c "
  from django.apps import apps
  local = [a.name for a in apps.get_app_configs() if a.name.startswith('src.')]
  print(sorted(local))
  "
  ```
- [x] **Expected:** `['src.blog', 'src.catalogue', 'src.core', 'src.inquiry', 'src.pages']`
- [x] **On failure:** Open `base.py` and confirm all 5 `src.X` entries are present in `INSTALLED_APPS`. Confirm each app directory has an `apps.py` with `name = 'src.X'` matching the dotted path.

---

### 5.5 Configure i18n settings for `modeltranslation`

#### Step 5.5.1: Add `LANGUAGES`, `LANGUAGE_CODE`, and `MODELTRANSLATION_*` to `base.py`

- [x] **Action:** Edit `backend/web_app/settings/base.py`. Replace the existing i18n block and add `modeltranslation` settings:

  ```python
  # Before:
  LANGUAGE_CODE = 'pl-pl'
  TIME_ZONE = 'Europe/Warsaw'
  USE_I18N = True
  USE_TZ = True

  # After:
  from django.utils.translation import gettext_lazy as _

  LANGUAGE_CODE = 'pl'        # must match a code in LANGUAGES exactly
  LANGUAGES = [
      ('pl', _('Polish')),
      ('en', _('English')),
  ]
  MODELTRANSLATION_DEFAULT_LANGUAGE = 'pl'
  MODELTRANSLATION_FALLBACK_LANGUAGES = ('pl',)

  TIME_ZONE = 'Europe/Warsaw'
  USE_I18N = True
  USE_TZ = True
  ```

  **Why `LANGUAGE_CODE = 'pl'` not `'pl-pl'`:** `modeltranslation` generates DB column suffixes from the language codes in `LANGUAGES` (e.g., `name_pl`, `name_en`). When `get_language()` is called, Django returns the active language code. If `LANGUAGE_CODE = 'pl-pl'` but `LANGUAGES` only contains `('pl', ...)`, Django may return `'pl-pl'` in certain middleware contexts and modeltranslation will fail to find the `_pl-pl` column (because it doesn't exist — only `_pl` does). Setting `LANGUAGE_CODE = 'pl'` ensures exact match.

  **Why `MODELTRANSLATION_FALLBACK_LANGUAGES = ('pl',)`:** If a field's English translation is empty, fall back to Polish. This prevents `None` from appearing on the frontend when a translator hasn't filled in the English version yet.

  **Why import `gettext_lazy`:** `LANGUAGES` values must be lazy-translated strings so they render correctly in the admin locale switcher. The `_()` wrapper enables this.

- [x] **Validate:**
  ```bash
  cd backend && python manage.py shell -c "
  from django.conf import settings
  print('LANGUAGE_CODE:', settings.LANGUAGE_CODE)
  print('LANGUAGES:', settings.LANGUAGES)
  print('DEFAULT_LANG:', settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
  print('FALLBACK:', settings.MODELTRANSLATION_FALLBACK_LANGUAGES)
  "
  ```
- [x] **Expected:**
  ```
  LANGUAGE_CODE: pl
  LANGUAGES: [('pl', 'Polish'), ('en', 'English')]
  DEFAULT_LANG: pl
  FALLBACK: ('pl',)
  ```
  (The `_('Polish')` lazy string renders as `'Polish'` in the shell — or `'polski'`/`'angielski'` in a Polish-locale Docker env. Both are correct.)
- [x] **On failure:** Confirm `from django.utils.translation import gettext_lazy as _` is at the top of `base.py`. Confirm `LANGUAGE_CODE = 'pl'` (not `'pl-pl'`). If `ModuleNotFoundError: No module named 'modeltranslation'` — run `pip install django-modeltranslation`.

---

### 5.6 Configure `drf-spectacular` for orval compatibility

#### Step 5.6.1: Add `COMPONENT_SPLIT_REQUEST` and `SERVE_INCLUDE_SCHEMA` to `SPECTACULAR_SETTINGS`

- [x] **Action:** Edit `backend/web_app/settings/base.py`. Replace the existing `SPECTACULAR_SETTINGS` block:

  ```python
  # Before:
  SPECTACULAR_SETTINGS = {
      'TITLE': 'Warsaw Costume Rental API',
      'DESCRIPTION': 'API dla aplikacji wypożyczalni kostiumów.',
      'VERSION': '1.0.0',
  }

  # After:
  SPECTACULAR_SETTINGS = {
      'TITLE': 'Warsaw Costume Rental API',
      'DESCRIPTION': 'API dla aplikacji wypożyczalni kostiumów.',
      'VERSION': '1.0.0',
      'SERVE_INCLUDE_SCHEMA': False,
      'COMPONENT_SPLIT_REQUEST': True,
  }
  ```

  **Why `COMPONENT_SPLIT_REQUEST: True`:** Without this, drf-spectacular generates a single schema component that is used for both the request body (POST/PUT input) and the response body (GET output). For endpoints where input and output differ (e.g., `InquirySubmitView` takes `customer_name` but returns `id` + `status`), orval cannot infer which fields are required for writes vs. reads. With `COMPONENT_SPLIT_REQUEST: True`, drf-spectacular generates separate `XxxRequest` and `XxxResponse` components. Orval uses `XxxRequest` for mutation hooks and `XxxResponse` for query hooks — correct, non-overlapping types.

  **Why `SERVE_INCLUDE_SCHEMA: False`:** Prevents the `/api/schema/` endpoint itself from appearing as an operation in the generated schema. Without this, the schema describes how to fetch the schema, which is recursive noise in the orval-generated client.

- [x] **Validate:**
  ```bash
  cd backend && python manage.py shell -c "
  from django.conf import settings
  s = settings.SPECTACULAR_SETTINGS
  print('COMPONENT_SPLIT_REQUEST:', s.get('COMPONENT_SPLIT_REQUEST'))
  print('SERVE_INCLUDE_SCHEMA:', s.get('SERVE_INCLUDE_SCHEMA'))
  "
  ```
- [x] **Expected:**
  ```
  COMPONENT_SPLIT_REQUEST: True
  SERVE_INCLUDE_SCHEMA: False
  ```
- [x] **On failure:** Confirm you edited `base.py` and not `dev.py`. Check for syntax errors (missing comma after `'VERSION': '1.0.0',`).

---

### 5.7 Tighten CORS to port 5173

#### Step 5.7.1: Replace `CORS_ALLOW_ALL_ORIGINS` with scoped `CORS_ALLOWED_ORIGINS` in `dev.py`

- [x] **Action:** Edit `backend/web_app/settings/dev.py`. Also remove the fallback defaults from `os.environ.get()` so a missing `.env` fails loudly:

  ```python
  import os
  from .base import *

  DEBUG = True

  CORS_ALLOWED_ORIGINS = [
      'http://localhost:5173',
      'http://127.0.0.1:5173',
  ]

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': os.environ['DB_NAME'],
          'USER': os.environ['DB_USER'],
          'PASSWORD': os.environ['DB_PASS'],
          'HOST': os.environ.get('DB_HOST', 'localhost'),
          'PORT': '5432',
      }
  }
  ```

  **Note:** `DB_HOST` keeps `.get('DB_HOST', 'localhost')` as the only allowed default — `'localhost'` is the correct value for running Postgres locally (not via Docker). All other DB vars use `[]` (fail loud if `.env` not loaded).

  **Implication for frontend work:** The Vite dev server MUST run on port 5173 (the default). If you ever need to use a different port, add it to this list before starting `vite`. Requests from any other origin will be blocked by the browser's CORS preflight — Postman and curl bypass this restriction (they don't enforce CORS).

- [x] **Validate:**
  ```bash
  cd backend && python manage.py shell -c "
  from django.conf import settings
  print('CORS_ALLOWED_ORIGINS:', getattr(settings, 'CORS_ALLOWED_ORIGINS', 'NOT SET'))
  print('CORS_ALLOW_ALL_ORIGINS:', getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'NOT SET'))
  "
  ```
- [x] **Expected:**
  ```
  CORS_ALLOWED_ORIGINS: ['http://localhost:5173', 'http://127.0.0.1:5173']
  CORS_ALLOW_ALL_ORIGINS: NOT SET
  ```
- [x] **On failure:** Confirm `dev.py` is being used — check `DJANGO_SETTINGS_MODULE` env var. Confirm `CORS_ALLOW_ALL_ORIGINS` line was deleted (not just commented). If `KeyError: 'DB_NAME'` appears, the `.env` is not loading — revisit Step 5.1.1.

---

### 5.8 Write pytest smoke tests

#### Step 5.8.1: Create `backend/tests/test_settings_smoke.py`

- [x] **Action:** Create `backend/tests/test_settings_smoke.py`:

  ```python
  import pytest
  from django.conf import settings


  # ── Settings integrity ────────────────────────────────────────────────────────

  def test_installed_apps_contains_all_local_apps():
      expected = {'src.core', 'src.catalogue', 'src.blog', 'src.pages', 'src.inquiry'}
      assert expected.issubset(set(settings.INSTALLED_APPS))


  def test_modeltranslation_before_admin():
      apps = list(settings.INSTALLED_APPS)
      assert 'modeltranslation' in apps, "modeltranslation must be in INSTALLED_APPS"
      assert apps.index('modeltranslation') < apps.index('django.contrib.admin'), (
          "modeltranslation must appear before django.contrib.admin"
      )


  def test_drf_spectacular_in_installed_apps():
      assert 'drf_spectacular' in settings.INSTALLED_APPS


  def test_cors_middleware_is_first():
      assert settings.MIDDLEWARE[0] == 'corsheaders.middleware.CorsMiddleware', (
          f"CorsMiddleware must be first, got: {settings.MIDDLEWARE[0]}"
      )


  def test_secret_key_is_set_and_not_empty():
      assert settings.SECRET_KEY, "SECRET_KEY must not be empty"
      assert len(settings.SECRET_KEY) >= 20, "SECRET_KEY suspiciously short"


  def test_language_code_matches_languages():
      codes = [code for code, _ in settings.LANGUAGES]
      assert settings.LANGUAGE_CODE in codes, (
          f"LANGUAGE_CODE '{settings.LANGUAGE_CODE}' not found in LANGUAGES codes: {codes}"
      )


  def test_modeltranslation_default_language():
      assert settings.MODELTRANSLATION_DEFAULT_LANGUAGE == 'pl'


  def test_modeltranslation_fallback_languages():
      assert 'pl' in settings.MODELTRANSLATION_FALLBACK_LANGUAGES


  def test_spectacular_component_split_request():
      assert settings.SPECTACULAR_SETTINGS.get('COMPONENT_SPLIT_REQUEST') is True, (
          "COMPONENT_SPLIT_REQUEST must be True for orval compatibility"
      )


  def test_spectacular_serve_include_schema_false():
      assert settings.SPECTACULAR_SETTINGS.get('SERVE_INCLUDE_SCHEMA') is False


  def test_media_root_configured():
      assert settings.MEDIA_ROOT is not None
      assert 'media' in str(settings.MEDIA_ROOT).lower()


  def test_use_i18n_and_tz():
      assert settings.USE_I18N is True
      assert settings.USE_TZ is True
      assert settings.TIME_ZONE == 'Europe/Warsaw'


  # ── OpenAPI endpoints ─────────────────────────────────────────────────────────

  @pytest.mark.django_db
  def test_api_schema_returns_200(client):
      """
      /api/schema/ must return 200.
      This endpoint is the contract for orval in issue #14.
      A 404 means drf_spectacular URLs are missing from urls.py.
      A 500 means a serializer or view has a misconfiguration.
      """
      response = client.get('/api/schema/')
      assert response.status_code == 200, (
          f"Expected 200, got {response.status_code}. "
          "Check that 'drf_spectacular' is in INSTALLED_APPS and "
          "SpectacularAPIView is wired in web_app/urls.py."
      )


  @pytest.mark.django_db
  def test_api_schema_content_type_is_openapi(client):
      response = client.get('/api/schema/')
      content_type = response.get('Content-Type', '')
      assert 'openapi' in content_type or 'yaml' in content_type or 'json' in content_type, (
          f"Unexpected Content-Type: {content_type}"
      )


  @pytest.mark.django_db
  def test_api_docs_returns_200(client):
      """
      /api/docs/ must return 200 HTML.
      A 404 means SpectacularSwaggerView is not wired in urls.py.
      """
      response = client.get('/api/docs/')
      assert response.status_code == 200, (
          f"Expected 200, got {response.status_code}. "
          "Check SpectacularSwaggerView in web_app/urls.py."
      )
      assert b'swagger' in response.content.lower() or b'openapi' in response.content.lower()


  @pytest.mark.django_db
  def test_database_connection():
      from django.db import connection
      with connection.cursor() as cursor:
          cursor.execute('SELECT 1')
          assert cursor.fetchone() == (1,)
  ```

- [x] **Validate:**
  ```bash
  cd backend && pytest tests/test_settings_smoke.py -v
  ```
- [x] **Expected:**
  ```
  tests/test_settings_smoke.py::test_installed_apps_contains_all_local_apps PASSED
  tests/test_settings_smoke.py::test_modeltranslation_before_admin PASSED
  tests/test_settings_smoke.py::test_drf_spectacular_in_installed_apps PASSED
  tests/test_settings_smoke.py::test_cors_middleware_is_first PASSED
  tests/test_settings_smoke.py::test_secret_key_is_set_and_not_empty PASSED
  tests/test_settings_smoke.py::test_language_code_matches_languages PASSED
  tests/test_settings_smoke.py::test_modeltranslation_default_language PASSED
  tests/test_settings_smoke.py::test_modeltranslation_fallback_languages PASSED
  tests/test_settings_smoke.py::test_spectacular_component_split_request PASSED
  tests/test_settings_smoke.py::test_spectacular_serve_include_schema_false PASSED
  tests/test_settings_smoke.py::test_media_root_configured PASSED
  tests/test_settings_smoke.py::test_use_i18n_and_tz PASSED
  tests/test_settings_smoke.py::test_api_schema_returns_200 PASSED
  tests/test_settings_smoke.py::test_api_schema_content_type_is_openapi PASSED
  tests/test_settings_smoke.py::test_api_docs_returns_200 PASSED
  tests/test_settings_smoke.py::test_database_connection PASSED

  16 passed in X.XXs
  ```
  Tests use `test.py` settings (SQLite in-memory) — no Docker needed for the test suite.
- [x] **On failure — per test:**
  - `test_modeltranslation_before_admin` → Step 5.4.1 incomplete.
  - `test_language_code_matches_languages` → `LANGUAGE_CODE` still `'pl-pl'`; fix Step 5.5.1.
  - `test_spectacular_component_split_request` → Step 5.6.1 incomplete.
  - `test_secret_key_is_set_and_not_empty` → `SECRET_KEY` still hardcoded or env not loading. Test settings (`test.py`) inherits from `base.py` which uses `os.environ['SECRET_KEY']`. The test runner (pytest) reads `pytest.ini` which points to `web_app.settings.test`. When pytest runs, `manage.py` is NOT invoked — so `load_dotenv()` from `manage.py` does NOT run. **You must ensure `SECRET_KEY` is available in the shell environment when running pytest**, OR add `load_dotenv()` to `test.py` as well. See step 5.8.2.
  - `test_api_schema_returns_200` → 404: confirm `SpectacularAPIView` URL in `urls.py`. 500: check serializer imports.
  - `test_database_connection` → should always pass with SQLite in-memory.

#### Step 5.8.2: Fix `SECRET_KEY` availability during pytest

**Context:** pytest invokes `web_app.settings.test` directly (per `pytest.ini`). It does NOT call `manage.py`, so `load_dotenv()` from Step 5.1.1 does NOT run during test collection. If `base.py` has `SECRET_KEY = os.environ['SECRET_KEY']` and the env var is not set, pytest will crash on import.

- [x] **Action:** Add `load_dotenv()` to the top of `backend/web_app/settings/test.py` (before `from .base import *`):

  ```python
  from pathlib import Path
  from dotenv import load_dotenv

  load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / '.env')

  from .base import *

  DEBUG = False

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': ':memory:',
      }
  }

  EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
  ```

  **Path resolution:** `Path(__file__).resolve()` = `backend/web_app/settings/test.py`. Three `.parent` calls → `backend/`. Four `.parent` calls → project root. `/ '.env'` → project root `.env`. ✅

- [x] **Validate:**
  ```bash
  cd backend && pytest tests/test_settings_smoke.py::test_secret_key_is_set_and_not_empty -v
  ```
- [x] **Expected:** `PASSED`
- [x] **On failure:** Print the resolved path to confirm it: `python -c "from pathlib import Path; p = Path('web_app/settings/test.py').resolve(); print(p.parents[3] / '.env')"`. Should point to the project root `.env`.

---

### 5.9 End-to-end validation

#### Step 5.9.0: Add schema.yaml to .gitignore PRZED uruchomieniem spectacular

- [x] Action: Edit .gitignore, add line:
  # Generated OpenAPI schema (regenerate via `manage.py spectacular`)
  schema.yaml
- [x] Validate: grep -c "^schema.yaml$" .gitignore
- [x] Expected: 1 (line 81 of .gitignore)
- [x] On failure: Add line manually

#### Step 5.9.1: `manage.py check`

- [x] **Action:** `cd backend && python manage.py check`
- [x] **Validate:** Read terminal output.
- [x] **Expected:** `System check identified no issues (0 silenced).`
- [x] **On failure:** Read the full error. Common causes: misspelled app name in `INSTALLED_APPS`, missing `apps.py` `name` field, bad import in `models.py`. Fix the reported issue before proceeding.

#### Step 5.9.2: Apply migrations against dev Postgres

- [x] **Action:**
  ```bash
  docker compose up db -d
  # Wait 3-5 seconds for Postgres to be ready, then:
  cd backend && python manage.py migrate
  ```
- [x] **Validate:** `cd backend && python manage.py showmigrations`
- [x] **Expected:** All entries show `[X]` (applied). This includes Django's built-in migrations (`admin`, `auth`, `contenttypes`, `sessions`) and all 5 local app migrations.
  ```
  admin
   [X] 0001_initial
  auth
   [X] 0001_initial
  ...
  catalogue
   [X] 0001_initial
   [X] 0002_...
  ...
  ```
- [x] **On failure:** `OperationalError: could not connect to server` → DB not running; confirm `docker compose up db -d` succeeded. `KeyError: 'DB_NAME'` → `.env` not loaded; revisit Step 5.1.1. Migration file syntax error → check the failing app's migration file.

#### Step 5.9.3: `runserver` starts without errors

- [x] **Action:** `cd backend && python manage.py runserver 0.0.0.0:8000`
- [x] **Validate:** Watch terminal for 5 seconds. Look for startup banner.
- [x] **Expected:**
  ```
  Django version X.X.X, using settings 'web_app.settings.dev'
  Starting development server at http://0.0.0.0:8000/
  Quit the server with CTRL-BREAK.
  ```
  No `ImproperlyConfigured`, no `ImportError`, no Python traceback.
- [x] **On failure:** Read the full traceback. Most common at this stage: `KeyError: 'SECRET_KEY'` (env not loaded — Step 5.1.1), `OperationalError` (DB not running — Step 5.9.2), `ModuleNotFoundError` (package not installed — run `pip install -r requirements.txt`).

#### Step 5.9.4: Verify admin and OpenAPI endpoints

Keep `runserver` running from Step 5.9.3. Open browser and verify each URL:

- [x] **`http://localhost:8000/admin/`**
  - **Expected:** Django admin login page renders. No 500. No template error.
  - **On failure:** Check `TEMPLATES` config in `base.py` (`APP_DIRS: True` required). If `ProgrammingError` → migrations not applied (Step 5.9.2 incomplete).

- [x] **`http://localhost:8000/api/schema/`**
  - **Expected:** YAML or JSON response (OpenAPI 3.0 schema). Status 200. The document contains the API title "Warsaw Costume Rental API".
  - **On failure:** 404 → confirm `SpectacularAPIView` path in `urls.py`. 500 → check `drf_spectacular` is in `INSTALLED_APPS`.

- [x] **`http://localhost:8000/api/docs/`**
  - **Expected:** Swagger UI page renders in browser. The page title shows "Warsaw Costume Rental API". No console errors about schema loading.
  - **On failure:** 404 → confirm `SpectacularSwaggerView` path in `urls.py`. Blank page with console errors → static files issue (acceptable for now in dev since static files are served by `runserver`; run `manage.py collectstatic` if needed).

#### Step 5.9.5: Generate schema file with zero warnings

- [x] **Action:** Stop `runserver`. Then:
  ```bash
  cd backend && python manage.py spectacular --file schema.yaml --validate
  ```
- [x] **Validate:** Read terminal output.
- [x] **Expected:**
  ```
  No issues found, schema is valid.
  ```
  File `backend/schema.yaml` is created. Zero lines beginning with `Warning:`.
  **Note (drf-spectacular 0.29.0):** When there are zero warnings/errors, the command exits silently with code 0. This is the success path.
- [x] **On failure:** Read each warning carefully.
  - `Warning: ... encountered unknown field` → a serializer field type is not supported by spectacular; add a `@extend_schema_field` decorator to the serializer field.
  - `Warning: could not resolve serializer` → a view's serializer_class is missing or set dynamically without annotation; add `@extend_schema(responses=MySerializer)` to the view.
  - These warnings are non-blocking for issue #1 (no real serializers exist yet), but any warnings from the scaffold itself (schema/docs views) must be zero.

  **Fixes applied:** Initial scaffold had 2 warnings (`get_image_url`, `get_main_image`) and 4 errors (`InitView`). Fixed by adding `@extend_schema_field` to both SerializerMethodFields and `@extend_schema(responses=inline_serializer(...))` to InitView.get().

  **Note:** Add `schema.yaml` to `.gitignore` since it is a generated artifact — it should be regenerated from source, not committed.

---

## 6. Deep analysis — skutki działań (holistycznie)

### 6.1 Wpływ na inne Django apps

- **`src.core`** — gains `modeltranslation` infrastructure. When issue #4 adds `SiteSettings` and `GlobalAlert` models, a `translation.py` file will register which fields are translated. No current migration is affected.
- **`src.catalogue`** — same. Future `translation.py` will add `name_pl`, `name_en`, `description_pl`, `description_en` columns to `catalogue_costume` and `catalogue_category` tables. All current migrations remain valid.
- **`src.blog`, `src.pages`** — same. Body/content fields (Markdown) may not be translated (TBD per those issues — full-body translation vs. a single-language editorial workflow). This decision is deferred to those issues.
- **`src.inquiry`** — `Inquiry` has no user-facing translated fields. Modeltranslation registration is not expected for this app.
- **Cross-app ordering invariant:** Once `modeltranslation` is in `INSTALLED_APPS` before `admin`, this ordering must be preserved forever. Any future reorganization of `INSTALLED_APPS` must respect this constraint.

### 6.2 Wpływ na bazę danych

- **No new tables** from this issue. `modeltranslation` creates no tables of its own — it only adds columns to app model tables when `TranslationOptions` classes are registered in `translation.py` files (done in per-model issues).
- **Existing migrations unchanged.** Current `0001_initial` migrations for all 5 apps remain valid.
- **First `migrate` run** creates Django built-in tables (`auth_*`, `django_*`, `admin_*`) if not already created.
- **`schema.yaml` artifact** is written to `backend/schema.yaml` by Step 5.9.5. Add `schema.yaml` to `.gitignore` (generated artifact, not source).
- **Migracje odwracalne?** Yes — no new migrations in this issue.

### 6.3 Wpływ na i18n (django-modeltranslation)

- **`LANGUAGES = [('pl', ...), ('en', ...)]`** defines the two supported content languages. This setting is the source of truth for which suffixed columns (`_pl`, `_en`) are generated.
- **`LANGUAGE_CODE = 'pl'`** is the server's default active language. It must exactly match one entry in `LANGUAGES` — the previous `'pl-pl'` value did NOT match and would cause silent mismatches when `get_language()` returns `'pl-pl'` in a middleware context.
- **`MODELTRANSLATION_DEFAULT_LANGUAGE = 'pl'`** tells modeltranslation which language column to use as the "canonical" value. When saving a model instance, if you set `obj.name = 'Kostium'`, it writes to `name_pl`. Polish is authoritative.
- **`MODELTRANSLATION_FALLBACK_LANGUAGES = ('pl',)`** means: if `name_en` is `None` or empty, return `name_pl` instead of `None`. Prevents null values from reaching the frontend before content is translated.
- **`LOCALE_PATHS` not required:** Django finds locale files automatically via `locale/` directories inside each app. No central `LOCALE_PATHS` needed unless you add project-level translations later.
- **Requires regenerating migrations after `translation.py`:** When a future issue adds `src/catalogue/translation.py`, running `makemigrations` will produce a new migration adding language columns. That migration is additive and non-destructive.

### 6.4 Wpływ na frontend (linkage to issue #14)

- **`/api/schema/` endpoint** created by this issue is the direct input to orval in issue #14. The pipeline will be:
  1. Dev starts backend → `GET /api/schema/` returns OpenAPI 3.0 YAML (or JSON)
  2. `orval` reads the schema → generates: TypeScript types, TanStack Query hooks, Zod validation schemas
  3. Frontend imports generated hooks (e.g., `useCostumeList()`) — no hand-written fetch code

- **`COMPONENT_SPLIT_REQUEST: True`** is essential for orval's mutation type generation. Without it, orval generates `XxxRequest` = `XxxResponse`, meaning write endpoints accept the same payload as they return (wrong for create/update endpoints where request and response differ). With it, orval generates distinct `XxxRequest` and `Xxx` types.

- **`SERVE_INCLUDE_SCHEMA: False`** prevents `/api/schema/` from appearing as a documented endpoint in its own output — avoids a recursive/circular reference that would pollute orval's generated output.

- **No Zod schemas written manually for API responses** — this is now a hard anti-pattern recorded in `docs/lessons-learned.md`. The only Zod schemas written by hand are for form validation where the input structure differs from the API response.

- **No TypeScript types or Zod changes in this issue** — zero frontend files modified. Issue #14 handles the full orval setup.

### 6.5 Wpływ na media / storage

- `MEDIA_ROOT = BASE_DIR / 'media'` resolves to `backend/media/`. This directory does not exist yet and is in `.gitignore`. Django creates it automatically on first file upload via an `ImageField` or `FileField`. No manual creation needed.
- `MEDIA_URL = '/media/'` is served by `runserver` in dev via the `static()` call in `urls.py`. Already wired.
- No new upload paths in this issue.

### 6.6 Wpływ na CORS / CSRF

- **Before:** `CORS_ALLOW_ALL_ORIGINS = True` — all browser origins accepted. Zero security in dev.
- **After:** `CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']` — only the Vite dev server port. Any other origin is blocked at the browser preflight stage.
- **Postman/curl:** Not affected by CORS (they are not browsers and do not send `Origin` preflight headers). API testing via Postman works regardless of `CORS_ALLOWED_ORIGINS`.
- **CSRF:** DRF views with `AllowAny` permission and no `SessionAuthentication` (all our read API views) do not require CSRF tokens from React. The `InquirySubmitView` (POST) will use DRF's `AllowAny` + `JSONParser` — no CSRF enforcement by DRF in this configuration. If session auth is ever added, revisit.
- **New endpoints in this issue:** `/api/schema/` and `/api/docs/` — both are `GET`-only, `AllowAny`, no CSRF concern.

---

## 7. Testing strategy

### 7.1 Unit tests (pytest-django)

All tests live in `backend/tests/test_settings_smoke.py` created in Step 5.8.1.

| Test | What it verifies |
|------|-----------------|
| `test_installed_apps_contains_all_local_apps` | All 5 `src.X` apps registered |
| `test_modeltranslation_before_admin` | Ordering constraint enforced |
| `test_drf_spectacular_in_installed_apps` | Schema generation possible |
| `test_cors_middleware_is_first` | CORS headers applied before any other middleware |
| `test_secret_key_is_set_and_not_empty` | Env loading works end-to-end |
| `test_language_code_matches_languages` | No `'pl-pl'` vs `'pl'` mismatch |
| `test_modeltranslation_default_language` | Canonical language is Polish |
| `test_modeltranslation_fallback_languages` | Empty EN fields fall back to PL |
| `test_spectacular_component_split_request` | orval compatibility setting present |
| `test_spectacular_serve_include_schema_false` | Schema self-reference absent |
| `test_media_root_configured` | File uploads will have a storage target |
| `test_use_i18n_and_tz` | Locale and timezone correct |
| `test_api_schema_returns_200` | `/api/schema/` endpoint live |
| `test_api_schema_content_type_is_openapi` | Response is actually an OpenAPI document |
| `test_api_docs_returns_200` | `/api/docs/` Swagger UI endpoint live |
| `test_database_connection` | SQLite in-memory DB reachable during tests |

### 7.2 Integration tests

- [ ] Django admin renders at `http://localhost:8000/admin/` (manual — browser)
- [ ] `http://localhost:8000/api/schema/` returns YAML with key `openapi: 3.0.x` (manual — browser or curl)
- [ ] `http://localhost:8000/api/docs/` renders Swagger UI HTML (manual — browser)
- [ ] `python manage.py spectacular --file schema.yaml --validate` produces zero warnings (automated — Step 5.9.5)

### 7.3 Manual QA checklist

- [ ] **Fresh clone test:** Clone the repo into a new directory → copy `.env.example` to `.env` → fill in values → `docker compose up db -d` → `pip install -r backend/requirements.txt` → `python manage.py migrate` → `python manage.py runserver` → confirm clean boot. This validates the onboarding contract in `.env.example`.
- [ ] Create a superuser: `python manage.py createsuperuser`. Log in to `/admin/`. Confirm all 5 app sections are visible in the sidebar (even if empty — admin registration is from earlier migrations).
- [ ] In browser, navigate to `/api/schema/` → download/view the YAML → confirm title is "Warsaw Costume Rental API" and `components` section is present (even if empty for now).
- [ ] In browser, navigate to `/api/docs/` → Swagger UI loads → "Warsaw Costume Rental API" appears in the title.

### 7.4 Test commands

```bash
# Run smoke tests (no Docker needed — uses SQLite in-memory via test.py)
cd backend
pytest tests/test_settings_smoke.py -v

# Run all tests
cd backend
pytest -v

# Run with coverage report
cd backend
pytest tests/test_settings_smoke.py --cov=web_app.settings --cov-report=term-missing

# Generate and validate OpenAPI schema (requires Docker DB running)
cd backend
python manage.py spectacular --file schema.yaml --validate
```

---

## 8. Rollback plan

**Jeśli coś pójdzie nie tak:**

1. `git stash` — reverts all uncommitted changes to `base.py`, `dev.py`, `manage.py`, `test.py`, and removes the new test file.
2. `.env.example` was not yet committed → simply delete it.
3. `.env` edits (added `SECRET_KEY`, `DB_HOST`) → manually remove those two lines from `.env`. The `.env` file itself is not committed so there is no git revert needed.
4. No migrations are created in this issue → no `migrate --fake` or backward migrations needed.
5. `schema.yaml` → delete the file (it's generated, not source).

**Unrecoverable state:** None. All changes in this issue are configuration files. No destructive DB operations. No committed secrets (`.env` stays gitignored). Full rollback is `git stash` + manual `.env` cleanup.

---

## 9. Open questions

- [ ] **`schema.yaml` committed or gitignored?** The `python manage.py spectacular --file schema.yaml` command in Step 5.9.5 writes a `schema.yaml` to `backend/`. For orval in issue #14, there are two options: (A) orval fetches the schema from a running backend at `http://localhost:8000/api/schema/` (requires backend running during FE build), (B) orval reads a committed `schema.yaml` file (schema as artifact). Option A is simpler for development; Option B works offline. **Recommendation:** Use Option A for now (orval fetches live schema). Keep `schema.yaml` in `.gitignore`. Decide definitively in issue #14.

- [ ] **`ALLOWED_HOSTS`:** Currently `ALLOWED_HOSTS = []` in `base.py`. In Django, an empty list with `DEBUG = True` means all hosts are allowed. In `test.py`, `DEBUG = False` — but the test client bypasses `ALLOWED_HOSTS` enforcement. This is acceptable for now. For production settings (future issue), `ALLOWED_HOSTS` must be explicitly set.

- [ ] **`blog` and `pages` translation scope:** `docs/lessons-learned.md` and `CLAUDE.md` indicate that `content`/`body` fields in `blog` and `pages` apps use Markdown. Should these be translatable (requiring `content_pl` and `content_en` in DB) or single-language? Decision deferred to issues #5 and #6. The current i18n setup (`LANGUAGES = [('pl', ...), ('en', ...)]`) supports either option without rework.

---

## 10. Progress log

| Date | Step | What was done | Blockers | Notes |
|------|------|---------------|----------|-------|
| 2026-04-23 | — | Initial scaffold committed (959a111): all 5 apps, split settings, requirements, pytest.ini, docker-compose, .gitignore | — | ~75% of scope done in one commit |
| 2026-04-23 | Plan v1 | First plan written | drf_spectacular open question | Resolved in v2 |
| 2026-04-23 | Plan v2 | Plan regenerated with new "drf-spectacular is intentional" architectural decision; added LANGUAGES, MODELTRANSLATION_*, COMPONENT_SPLIT_REQUEST, scoped CORS, SECRET_KEY loading, 16 smoke tests | — | This document |
| 2026-04-26 | 5.1 | Added load_dotenv() to manage.py — Path resolves to project root .env; validated via Docker (DB_NAME=django_db printed correctly) | No local venv — all validation done via Docker | docker-compose environment vars pre-populate os.environ so load_dotenv is safe no-op in container |
| 2026-04-26 | 5.2 | Added SECRET_KEY and DB_HOST to .env; changed base.py to os.environ['SECRET_KEY']; added SECRET_KEY=${SECRET_KEY} to docker-compose.yml api environment | docker-compose.yml needed SECRET_KEY added (not in original plan scope — necessary implication) | Validated via Docker: settings.SECRET_KEY[:30] = django-insecure-d67553cq8)p5vc |
| 2026-04-26 | 5.3 | Created .env.example with all 5 keys; verified .gitignore has .env (line 47) and !.env.example (line 52) | — | — |
| 2026-04-26 | 5.4 | Added 'modeltranslation' at index 0 in INSTALLED_APPS; validated index=0 admin=1 OK; all 5 src.* apps confirmed | — | — |
| 2026-04-26 | 5.5 | Fixed LANGUAGE_CODE pl-pl→pl; added LANGUAGES, MODELTRANSLATION_DEFAULT_LANGUAGE, MODELTRANSLATION_FALLBACK_LANGUAGES; gettext_lazy import in settings | — | LANGUAGES rendered as polski/angielski in Docker Polish locale — correct behavior |
| 2026-04-26 | 5.6 | Added SERVE_INCLUDE_SCHEMA=False and COMPONENT_SPLIT_REQUEST=True to SPECTACULAR_SETTINGS | — | Validated via Docker — both values correct |
| 2026-04-26 | 5.7 | Replaced CORS_ALLOW_ALL_ORIGINS with CORS_ALLOWED_ORIGINS scoped to localhost:5173; removed fallback defaults from DB env vars (except DB_HOST) | — | Validated: CORS_ALLOW_ALL_ORIGINS=NOT SET |
| 2026-04-26 | 5.8 | Created test_settings_smoke.py (16 tests); added load_dotenv() to test.py for SECRET_KEY availability during pytest | — | **16 passed, 0 failed** via Docker with DJANGO_SETTINGS_MODULE=web_app.settings.test |
| 2026-04-26 | 5.9.0 | Added schema.yaml to .gitignore (line 81) | — | — |
| 2026-04-26 | 5.9.1 | manage.py check → "System check identified no issues (0 silenced)" | — | Via Docker --no-deps |
| 2026-04-26 | 5.9.2 | Migrations already applied from previous session; showmigrations shows all [X] | — | — |
| 2026-04-26 | 5.9.3 | runserver via Docker api service; Django 6.0.4 started at 0.0.0.0:8000, no traceback | — | — |
| 2026-04-26 | 5.9.4 | admin=200, /api/schema/=200 (openapi 3.0.3 + Warsaw Costume Rental API title), /api/docs/=200 (swagger UI) | — | Checked via Invoke-WebRequest from host |
| 2026-04-26 | 5.9.5 | spectacular --validate: exit 0, no warnings; schema.yaml created; gitignored. Required fixes: @extend_schema_field on get_image_url + get_main_image; @extend_schema on InitView.get() | Initial scaffold had 2 warnings + 4 errors — fixed as part of end-to-end validation | drf-spectacular 0.29.0 exits silently on success (no "No issues found" message) |

---

## 11. Definition of Done

**Wszystkie poniższe MUSZĄ być spełnione przed zamknięciem issue:**

- [ ] `.env.example` exists at project root and contains all 5 keys: `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `SECRET_KEY`
- [ ] `SECRET_KEY` is NOT hardcoded anywhere in `*.py` files — confirmed by `grep -r "django-insecure" backend/` returning zero results
- [ ] `python manage.py check` outputs `System check identified no issues (0 silenced).`
- [ ] `python manage.py runserver` starts without any traceback
- [ ] `http://localhost:8000/admin/` renders Django admin login page
- [ ] `http://localhost:8000/api/schema/` returns HTTP 200 with OpenAPI 3.0 content
- [ ] `http://localhost:8000/api/docs/` returns HTTP 200 with Swagger UI HTML
- [ ] `python manage.py spectacular --file schema.yaml --validate` outputs `No issues found, schema is valid.` with zero warning lines
- [ ] `pytest tests/test_settings_smoke.py -v` → **16 passed, 0 failed**
- [ ] `pytest -v` (entire test suite) → 0 failed
- [ ] `modeltranslation` appears in `INSTALLED_APPS` before `django.contrib.admin` — confirmed by `test_modeltranslation_before_admin` passing
- [ ] `LANGUAGE_CODE = 'pl'` (not `'pl-pl'`) — confirmed by `test_language_code_matches_languages` passing
- [ ] `SPECTACULAR_SETTINGS['COMPONENT_SPLIT_REQUEST'] is True` — confirmed by `test_spectacular_component_split_request` passing
- [ ] `CORS_ALLOW_ALL_ORIGINS` does NOT appear in any settings file — confirmed by `grep -r "CORS_ALLOW_ALL_ORIGINS" backend/` returning zero results
- [ ] `.env` is NOT committed — confirmed by `git status` showing no `.env` file
- [ ] `.env.example` IS committed — confirmed by `git status` showing `.env.example` or `git ls-files .env.example` returning the file
- [ ] `schema.yaml` is in `.gitignore` (generated artifact)
- [ ] All commits use conventional commits format (`chore:`, `fix:`, `feat:`, `test:`)
- [ ] Issue closed: `gh issue close 1 --comment "Done — see docs/plans/GH-1-django-project-setup.md"`
- [ ] This plan updated: `Status: 🟢 Done`, `Actual effort: X`

---

## 12. Post-mortem (wypełnij po zakończeniu)

**What went well:** All 16 smoke tests passed on first run after implementing all settings changes. Plan was clear and step-by-step structure made progress easy to track.
**What went wrong:** (1) No local venv existed — validation adapted to Docker throughout. (2) Initial scaffold had 2 warnings + 4 errors in spectacular that needed fixing (missing @extend_schema_field and @extend_schema annotations). (3) drf-spectacular 0.29.0 exits silently on success — plan expected "No issues found" text. (4) SECRET_KEY missing from docker-compose.yml api environment — added as part of step 5.2.
**Lessons learned:** See docs/lessons-learned.md — add: always annotate SerializerMethodFields with @extend_schema_field; always annotate bare APIViews with @extend_schema.
**Follow-up issues:** §9 question on blog/pages translation scope (issue #5/#6). Docker venv pre-condition should be clarified in future plans.
