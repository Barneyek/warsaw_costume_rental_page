# Lessons Learned — Warsaw Costume Rental

> **Purpose:** Zbiór lekcji, anti-patterns i wniosków z pracy nad projektem.
> Aktualizowane po każdej sesji / zamknięciu issue (przez `/dev-compound` lub ręcznie).
>
> **For Claude:** Przeczytaj ten plik zanim zaczniesz sesję. Unikaj wzorców oznaczonych jako ❌.

---

## 📚 Spis treści

- [Architecture decisions](#architecture-decisions)
- [Django / Backend](#django--backend)
- [React / Frontend](#react--frontend)
- [DevOps / Tooling](#devops--tooling)
- [AI Workflow](#ai-workflow)
- [Anti-patterns (avoid)](#anti-patterns)

---

## Architecture decisions

<!-- Format: ### Decision: <what>, Date: YYYY-MM-DD, Why, Alternatives considered, Trade-offs -->

### ✅ Decision: Full dotted paths `src.X` for Django apps
- **Date:** 2026-04-XX
- **Why:** Explicit imports, no ambiguity with nested modules, clear project boundary
- **Alternatives:** Flat app paths (`catalogue` without `src.`)
- **Trade-offs:** Trochę dłuższe ścieżki w `INSTALLED_APPS`, ale za to zero konfliktów nazw

### ✅ Decision: Zod for API types + runtime validation
- **Date:** 2026-04-23
- **Why:** Backend jest single source of truth dla kontraktu API. drf-spectacular auto-generuje OpenAPI schema z DRF serializers. orval czyta OpenAPI i generuje: (1) TS types, (2) hooki TanStack Query, (3) Zod schemas dla runtime validation. Żadnego ręcznego sync — zmiana w backendzie → regenerate → frontend dostaje update kontraktu.
- **Alternatives considered:**
  - Tylko Zod manual (prostsze, ale manual sync = źródło błędów przy 15-40 endpointach)
  - drf-spectacular + openapi-typescript bez orval (brak runtime validation)
- **Trade-offs:** +2h na setup orval config + CI step do regeneracji. Zysk: pełny type safety od DB po UI + portfolio-grade architecture.
- **Replaces:** poprzednia decyzja "Zod only, no OpenAPI" (była podjęta przed dodaniem TanStack Query do stacku — zmieniony kontekst).

### ✅ Decision: orval reads OpenAPI schema live from backend (Option A)
- **Date:** 2026-04-23
- **Why:** Solo dev project — orval invoked manually via `npm run gen:api` on frontend after backend changes. Schema fetched live from `http://localhost:8000/api/schema/`. No need to commit a static schema artifact.
- **Implication:** `schema.yaml` is NEVER committed. Added to `.gitignore`. The file is generated locally only for validation purposes (`python manage.py spectacular --validate`).
- **Alternatives considered:**
  - Option B: commit `schema.yaml` and have orval read from disk. Rejected — solo project, frontend always runs with backend, extra discipline overhead (must remember to regenerate before commit).
- **Workflow:** Backend running (`runserver`) → on FE run `npm run gen:api` → orval hits `/api/schema/` → generates TS types + TanStack Query hooks + Zod schemas. The npm script will be set up in issue #14.

### ✅ Decision: No OpenAPI exposure
- **Date:** 2026-04-XX
- **Why:** Deliberate architectural choice — used separately in another project
- **Alternatives:** Auto-generate types from OpenAPI schema
- **Trade-offs:** Ręczna synchronizacja Zod <> DRF, ale też większa kontrola

---

## Django / Backend

<!-- Dodaj w trakcie pracy -->

_No entries yet._

---

## React / Frontend

<!-- Dodaj w trakcie pracy -->

_No entries yet._

---

## DevOps / Tooling

### ✅ Git workflow
- **Branch model:** trunk-based (`main` only) — learning project, solo dev
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`)
- **Issue → Plan → Implementation → Close** — każde issue ma plan w `docs/plans/GH-N-*.md`

---

## AI Workflow

### ✅ Workflow: Issue → Plan → Implement → Close
1. Create issue on GitHub (title + body with acceptance criteria)
2. In Claude Code: generate plan in `docs/plans/GH-N-*.md` from issue
3. Review plan (self or discuss with claude.ai web)
4. Implement step-by-step, marking progress in plan
5. Close issue with reference to plan

### 📝 Prompt patterns that work
- **Plan generation:** *"Read issue #N via `gh issue view N` and generate plan in docs/plans/GH-N-*.md following `docs/plans/_template.md`. Fill every section. Ultrathink."*
- **Implementation:** *"Implement phase X from docs/plans/GH-N-*.md. Mark progress as you go. Do not skip validation steps."*

### ⚠️ Prompt patterns to avoid
_Dodaj w trakcie_

---

## Anti-patterns

<!-- Rzeczy których NIE robić w tym projekcie -->

### ❌ Don't: Skip validation steps in plan
**Why bad:** Validation per step jest po to, żeby AI (i Ty) wiedzieli że krok faktycznie zadziałał, a nie tylko został wykonany.
**Instead do:** Zawsze uruchom `validate` command, porównaj z `expected` przed oznaczeniem `[x]`.

### ❌ Don't: Commit `.env` or secrets
**Why bad:** Secret w repo = public leak (nawet w private repo — może być przypadkiem pushnięte na publiczne).
**Instead do:** `.env.example` w repo, real `.env` w `.gitignore`.

### ❌ Don't: Write Zod schemas manually for API responses
**Why bad:** Zod schemas dla API response są generowane przez orval z OpenAPI schema. Ręczne pisanie = duplikacja + desync z backendem.
**Instead do:** Po zmianie serializera w backendzie uruchom pipeline regeneracji (backend emituje openapi.yaml → orval generuje FE). Zod schemas tworzone ręcznie TYLKO dla form validation (jeśli formularz ma inną walidację niż API response).

### ❌ Don't: Commit `schema.yaml` to repo
**Why bad:** Generated artifact, will get stale, creates merge conflicts in PRs that touch serializers. Source of truth = DRF code.
**Instead do:** `schema.yaml` is in `.gitignore`. Frontend orval fetches from `/api/schema/` live.

<!-- Dodawaj w trakcie w miarę wpadek -->