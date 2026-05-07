# Warsaw Costume Rental — Project Brief

**Goal:** Scalable decoupled (headless CMS) web application — costume rental service. Educational / learning project.

**Focus:** Clean data architecture, asynchronous API communication, modern UX, AI-assisted workflow.

---

## 🏗️ Backend (Django + DRF)

### 1. core (system glue)
- **Purpose:** Global config, frontend ↔ backend "handshake".
- **Models:**
  - `SiteSettings` (Singleton): contacts, social media, global email.
  - `GlobalAlert`: messages with `valid_from`, `valid_until` (auto-scheduling), `is_active`.
- **API:** `/api/init/` — returns site config on frontend app boot.

### 2. catalogue (system core)
- **Models:**
  - `Category` (name, slug, parent_category)
  - `Tag` (simple labels, e.g., "Halloween")
  - `Size` (predefined size list)
  - `Costume`:
    - Fields: name, description, slug, price, deposit, is_active, is_available
    - Relations: `category` (FK), `tags` (M2M), `sizes` (M2M)
  - `CostumeImage`: 1:N relation to Costume
- **Media:**
  - Upload with UUID to `costumes/%Y/%m/%d/`
  - Pillow / django-imagekit — auto-thumbnail generation
- **API:** `/api/costumes/` with `django-filter` (category, size, tag) + `PageNumberPagination`

### 3. blog & pages (content)
- **blog:** News/announcements, `/api/news/`
- **pages:** Static pages (About, Terms); `content` field in Markdown, frontend renders via `react-markdown`

### 4. inquiry (request system)
- **Model:** `Inquiry` (customer_name, customer_email, message, status [new/read/replied], created_at)
- **Relation:** `items` (M2M to Costume) — track which costumes the customer asked about
- **Logic:** `/api/inquiry/submit/` saves to DB, then `services.py` sends email notifications

---

## 💻 Frontend (React + Vite + TypeScript)

- **Routing:** **TanStack Router** (file-based, type-safe). Replaces the originally planned `react-router-dom` — chosen for stack consistency with TanStack Query and end-to-end type safety. See `docs/lessons-learned.md` → "Decyzja: TanStack Router zamiast react-router-dom".
- **Data fetching:** TanStack Query (React Query). Generated hooks via orval (from `/api/schema/`).
- **Type safety pipeline:** drf-spectacular → orval → generated TS types + TanStack Query hooks + Zod schemas. No manual API type definitions.
- **State management:** Context API + `localStorage` for "schowek" (wishlist — selected costumes persist across reloads).
- **Styling:** Tailwind CSS — utility-first, fast iteration, no naming overhead.
- **i18n:** Backend sends both languages (`name_pl`, `name_en`); React decides which to display based on UI state.

---

## 🛠️ Tech checklist

1. **CORS:** `django-cors-headers` configured for Vite dev port (5173).
2. **i18n:** `django-modeltranslation` for translatable model fields. ⚠️ Must be FIRST in `INSTALLED_APPS`.
3. **Admin:** `TabularInline` for images, `filter_horizontal` for sizes/tags, status workflow for inquiries.
4. **Serializers:** Language mapping logic, full media URLs in responses.
5. **OpenAPI:** drf-spectacular schema at `/api/schema/`, Swagger UI at `/api/docs/`. `COMPONENT_SPLIT_REQUEST: True` for orval compatibility.
6. **Frontend type generation:** orval reads `/api/schema/` live (Option A — no static schema artifact committed).

---

## 📅 Implementation roadmap

> Status updated 2026-05-07 based on backend audit (see local `docs/audits/2026-05-07-backend-state-audit.md`).
> Initial scaffold (commit 959a111) included substantial implementation of models, serializers, views, URLs and filters across all 5 apps. Many "build" issues are now "audit + complete" issues.
>
> **Numbering note:** Roadmap items use **placeholder numbers** (`#1`-`#23`) reflecting planning order. **Audit-discovered work** uses symbolic names (`AUDIT-1`, `AUDIT-2`, …) because GitHub assigns real issue numbers from a pool shared with PRs — actual numbers are recorded next to symbolic names once an issue is created.

### Phase 0 — Foundation
- [x] **#1** [setup] Django project setup with split settings, drf-spectacular config, smoke tests — 🟢 **Done**
- [ ] **#2** [setup] Frontend scaffold — React + Vite + TS + TanStack Query + TanStack Router + Tailwind + smoke orval — 🔴 **Not started**
- [ ] **#3** [infra] Docker Compose — db + backend + frontend in one command — 🟡 **Partial** (db + api OK, frontend service missing)

### Phase 1 — Domain models (mostly done in scaffold)
- [x] **#4** [core] SiteSettings + GlobalAlert models + admin — 🟢 **Done**
- [ ] **#5** [catalogue] Category, Tag, Size, Costume, CostumeImage — 🟡 **Partial** (BUG-1 fixed via AUDIT-1)
- [x] **#6** [blog] NewsPost model + admin — 🟢 **Done**
- [ ] **#7** [pages] Page model — 🟡 **Partial** (no list endpoint — see AUDIT-3)
- [x] **#8** [inquiry] Inquiry model + M2M to Costume — 🟢 **Done**

### Phase 2 — API (mostly done in scaffold)
- [x] **#9** [api] /api/init/ endpoint — 🟢 **Done** (with @extend_schema)
- [x] **#10** [api] /api/costumes/ with filtering + pagination — 🟢 **Done**
- [x] **#11** [api] /api/news/ blog endpoint — 🟢 **Done**
- [ ] **#12** [api] /api/pages/ — 🟡 **Partial** (only detail, list missing — see AUDIT-3)
- [ ] **#13** [api] /api/inquiry/submit/ + email service — 🟡 **Partial** (DB save OK, email missing — see AUDIT-2)

### Phase 3 — Frontend integration
- [ ] **#14** [fe-api] orval generation pipeline + npm script `gen:api` — 🔴 **Not started**
- [ ] **#15** [fe] Costume catalog page + filtering — 🔴 **Not started**
- [ ] **#16** [fe] Costume detail page — 🔴 **Not started**
- [ ] **#17** [fe] Schowek (wishlist) — Context API + localStorage — 🔴 **Not started**
- [ ] **#18** [fe] Inquiry form — 🔴 **Not started**
- [ ] **#19** [fe] Blog page + Pages (Markdown via react-markdown) — 🔴 **Not started**
- [ ] **#20** [fe] i18n toggle PL/EN — 🔴 **Not started** (depends on AUDIT-4)

### Phase 4 — Polish & gaps from audit
- [ ] **#21** [tests] Pytest suite for backend — 🟡 **Partial** (30 tests exist, coverage to be verified)
- [ ] **#22** [media] Thumbnails via django-imagekit — 🔴 **Not started** (lib installed, not wired)
- [ ] **#23** [deploy] Deployment (optional) — 🔴 **Not started**

### Audit-driven issues (numbers assigned at creation)

> GitHub issue numbers are assigned at creation and shared with PR numbers. We track these by symbolic name and update with the real number when created. Status reflects current state.

| Symbolic | Description | GH issue # | PR | Status |
|----------|-------------|------------|------|--------|
| **AUDIT-1** | [hotfix] Add missing `timezone` import in `catalogue/models.py` (BUG-1) | #6 | #7 | 🟢 **Done** |
| **AUDIT-2** | [feat] Inquiry email service via `inquiry/services.py` (GAP-2) | _tbd_ | — | 🔴 **Not started** |
| **AUDIT-3** | [feat] Add `GET /api/pages/` list endpoint (GAP-3) | _tbd_ | — | 🔴 **Not started** |
| **AUDIT-4** | [feat] Translation files (`translation.py`) for all 5 apps + migrations (GAP-1, blocker for #20) | _tbd_ | — | 🔴 **Not started** |