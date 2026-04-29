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

- **State management:** Context API + `localStorage` for "schowek" (wishlist — selected costumes persist across reloads).
- **Type safety:** drf-spectacular → orval → generated TS types + TanStack Query hooks + Zod schemas. No manual API type definitions.
- **i18n:** Backend sends both languages (`name_pl`, `name_en`); React decides which to display based on UI state.
- **Routing:** `react-router-dom` for navigation between catalog, news, and static pages.

---

## 🛠️ Tech checklist

1. **CORS:** `django-cors-headers` configured for Vite dev port (5173).
2. **i18n:** `django-modeltranslation` for translatable model fields. ⚠️ Must be FIRST in `INSTALLED_APPS`.
3. **Admin:** `TabularInline` for images, `filter_horizontal` for sizes/tags, status workflow for inquiries.
4. **Serializers:** Language mapping logic, full media URLs in responses.
5. **OpenAPI:** drf-spectacular schema at `/api/schema/`, Swagger UI at `/api/docs/`. `COMPONENT_SPLIT_REQUEST: True` for orval compatibility.
6. **Frontend type generation:** orval reads `/api/schema/` live (Option A — no static schema artifact committed).

---

## 📅 Implementation roadmap (23 issues)

### Phase 0 — Foundation
- [x] **#1** [setup] Django project setup with split settings, drf-spectacular config, smoke tests
- [ ] **#2** [setup] Frontend scaffold — React + Vite + TS + TanStack Query + orval
- [ ] **#3** [infra] Docker Compose — db + backend + frontend in one command

### Phase 1 — Domain models
- [ ] **#4** [core] SiteSettings + GlobalAlert models + admin
- [ ] **#5** [catalogue] Category, Tag, Size, Costume, CostumeImage models
- [ ] **#6** [blog] Blog model + admin
- [ ] **#7** [pages] Page model (Markdown content) + admin
- [ ] **#8** [inquiry] Inquiry model + M2M to Costume

### Phase 2 — API
- [ ] **#9** [api] /api/init/ endpoint (SiteSettings + GlobalAlert)
- [ ] **#10** [api] /api/costumes/ with filtering + pagination + drf-spectacular schema
- [ ] **#11** [api] /api/news/ blog endpoint
- [ ] **#12** [api] /api/pages/ pages endpoint
- [ ] **#13** [api] /api/inquiry/submit/ + email service

### Phase 3 — Frontend integration
- [ ] **#14** [fe-api] orval generation pipeline + npm script `gen:api`
- [ ] **#15** [fe] Costume catalog page + filtering
- [ ] **#16** [fe] Costume detail page
- [ ] **#17** [fe] Schowek (wishlist) — Context API + localStorage
- [ ] **#18** [fe] Inquiry form
- [ ] **#19** [fe] Blog page + Pages (Markdown via react-markdown)
- [ ] **#20** [fe] i18n toggle PL/EN

### Phase 4 — Polish
- [ ] **#21** [tests] Pytest suite for backend
- [ ] **#22** [media] Thumbnails via django-imagekit
- [ ] **#23** [deploy] Deployment (optional)