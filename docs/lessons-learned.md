# Lessons Learned — Warsaw Costume Rental

> **Cel:** Zbiór lekcji, anti-patternów i wniosków z pracy nad projektem.
> Aktualizowane po każdej sesji / zamknięciu issue.

---

## 📚 Spis treści

- [Konwencje projektu](#konwencje-projektu)
- [Decyzje architektoniczne](#decyzje-architektoniczne)
- [Django / Backend](#django--backend)
- [React / Frontend](#react--frontend)
- [DevOps / Tooling](#devops--tooling)
- [AI Workflow](#ai-workflow)
- [Anti-patterns](#anti-patterns)

---

## Konwencje projektu

### 🌐 Język w plikach projektu

| Plik | Język | Powód |
|------|-------|-------|
| `README.md` | EN | Publiczna twarz repo |
| Kod (zmienne, komentarze) | EN | Branżowy standard |
| Commit messages | EN (`feat:`, `fix:`, ...) | Conventional Commits |
| GitHub Issues (title + body) | EN | Spójność |
| `CLAUDE.md` | EN | Konsumowane przez AI, branżowe terminy |
| `docs/PROJECT-BRIEF.md` | EN | Spójność z CLAUDE.md |
| **`docs/plans/GH-N-*.md`** | **PL** (treść) + EN (struktura, kod) | Notatki techniczne dla Ciebie. Sekcje, sub-sekcje i etykiety `Action`/`Validate`/`Expected`/`On failure` zostają EN — działają jak sygnały strukturalne. Treść opisowa, uzasadnienia, "Why" — po polsku. Fragmenty kodu, komendy terminala, nazwy techniczne (`branch`, `serializer`, `pull request`) zostają EN. |
| **`docs/lessons-learned.md`** | **PL** | Twoje notatki, dla Ciebie |

**Wyjątek historyczny:** `docs/plans/GH-1-django-project-setup.md` jest po angielsku — pierwszy plan, przed ustaleniem konwencji. Zostaje jak jest jako dokument historyczny.

### 🔧 Konwencje techniczne

- **Ścieżki Django apps:** pełne dotted paths (`src.catalogue`, nie `catalogue`).
- **Settings:** split na `base.py` + `dev.py` + `test.py` w `backend/web_app/settings/`.
- **Conventional Commits:** zawsze (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`).
- **Branch flow (od issue #2):** branch per issue + PR + squash merge. Issue #1 historycznie poszło na `main`.

---

## Decyzje architektoniczne

### ✅ Decyzja: Pełne ścieżki `src.X` dla Django apps
- **Data:** -- (przed #1)
- **Dlaczego:** Jednoznaczne importy, brak konfliktów nazw z bibliotekami, jasna granica projektowa.
- **Alternatywy rozważone:** Płaskie ścieżki (`catalogue` zamiast `src.catalogue`).
- **Kompromis:** Trochę dłuższe wpisy w `INSTALLED_APPS` — w zamian zero ambiguity.

### ✅ Decyzja: drf-spectacular + orval + Zod (pełny type safety)
- **Data:** 2026-04-23
- **Dlaczego:** Backend = single source of truth dla kontraktu API. drf-spectacular auto-generuje OpenAPI schema z DRF serializers. orval czyta OpenAPI i generuje na frontendzie: (1) typy TS, (2) hooki TanStack Query, (3) Zod schemas dla runtime validation. Zero ręcznego sync — zmiana w backendzie → regeneracja → frontend dostaje update kontraktu.
- **Alternatywy rozważone:**
  - Tylko Zod ręcznie (prostsze, ale ręczny sync = źródło błędów przy 15-40 endpointach).
  - drf-spectacular + openapi-typescript bez orval (brak runtime validation).
- **Kompromis:** +2h na setup orval + krok regeneracji. Zysk: pełny type safety od bazy po UI
- **Zastępuje:** Wcześniejszą decyzję "tylko Zod, no OpenAPI" (była podjęta przed dodaniem TanStack Query do stacku — zmienił się kontekst, decyzja zrewidowana).

### ✅ Decyzja: orval pobiera schemę live z backendu (Opcja A)
- **Data:** 2026-04-23
- **Dlaczego:** Solo dev project — orval odpalany ręcznie przez `npm run gen:api` na frontendzie po zmianach w backendzie. Schema fetchowana live z `http://localhost:8000/api/schema/`. Nie ma potrzeby commitować statycznego artefaktu.
- **Implikacja:** `schema.yaml` NIGDY nie jest commitowany. W `.gitignore`. Generowany lokalnie tylko do walidacji (`python manage.py spectacular --validate`).
- **Alternatywy rozważone:**
  - Opcja B: commit `schema.yaml` + orval czyta z dysku. Odrzucone — solo project, frontend i tak chodzi razem z backendem, dodatkowa dyscyplina (pamiętać o regeneracji przed commitem).
- **Workflow:** Backend działa (`runserver`) → na FE `npm run gen:api` → orval uderza w `/api/schema/` → generuje typy TS + hooki TanStack Query + Zod schemas. Skrypt `npm run gen:api` powstanie w issue #14.

### ✅ Decyzja: TanStack Router zamiast react-router-dom
- **Data:** 2026-04-23
- **Dlaczego:**
  - **Spójność stacku** — TanStack Query już jest w stacku, ten sam team / ta sama filozofia / native integration. Jedno spójne API zamiast dwóch różnych mechanizmów.
  - **Type safety** — full type-safe routing (params, search params, loaders typed). Pasuje do reszty: orval generuje typowane hooki, Zod waliduje runtime, drf-spectacular kontraktuje API. **Type-safety od bazy po nawigację.**
  - **Search params validated by schema** — costume catalog będzie miał filtry (`category`, `size`, `tag`) zapisane w URL. TanStack Router parsuje + waliduje search params przez schema, nie przez `string | undefined`.
  - **Edukacyjnie:** uczę się nowoczesnych wzorców, nie legacy. react-router-dom mogę nauczyć się w 2h w każdej chwili — to commodity. TanStack Router daje wyróżnik.
- **Alternatywy rozważone:**
  - **react-router-dom:** klasyk, ogromna społeczność, więcej tutoriali. Odrzucone — nie pasuje do type-safe stacku jaki budujemy.
- **Kompromis:** Mniej tutoriali / odpowiedzi na StackOverflow. Mniej AI muscle-memory. W praktyce — krzywa nauki +2-3 dni na początku.
- **Implikacja:** w `frontend/src/routes/` będzie file-based routing, plugin `@tanstack/router-vite-plugin` w Vite config.
- **Zastępuje:** wcześniejszą wzmiankę o `react-router-dom` w `PROJECT-BRIEF.md`.

---

## Django / Backend

### ⚠️ Pułapka: `modeltranslation` MUSI być przed `django.contrib.admin` w `INSTALLED_APPS`

- **Odkryte:** Issue #1
- **Objaw (cichy błąd):** Admin UI ładuje się, brak błędów, ale taby tłumaczeń nie pojawiają się po zarejestrowaniu `translation.py`.
- **Dlaczego:** `django-modeltranslation` monkey-patchuje `django.contrib.admin` w czasie importu. Jak admin załaduje się pierwszy, patch nie zostanie aplikowany.
- **Fix:** Pierwszy wpis w `INSTALLED_APPS` to zawsze `'modeltranslation'`.
- **Weryfikacja:** Smoke test `test_modeltranslation_before_admin` pilnuje kolejności.

### ⚠️ Pułapka: `LANGUAGE_CODE` MUSI dokładnie pasować do kodu z `LANGUAGES`

- **Odkryte:** Issue #1
- **Objaw (cichy błąd):** `LANGUAGE_CODE = 'pl-pl'` przy `LANGUAGES = [('pl', ...)]` powoduje że Django szuka kolumn `name_pl-pl`, których nie ma (istnieje tylko `name_pl`).
- **Fix:** Używaj `'pl'` konsekwentnie. Kody locale w obu ustawieniach muszą zgadzać się znak w znak.
- **Weryfikacja:** Smoke test `test_language_code_matches_languages`.

### ⚠️ Pułapka: `load_dotenv()` musi być w `manage.py` ORAZ `settings/test.py`

- **Odkryte:** Issue #1
- **Dlaczego:** pytest NIE odpala `manage.py` — importuje moduł settings bezpośrednio (z `pytest.ini`). Bez `load_dotenv()` na górze `test.py` zmienne env nie są wczytywane i testy crashują na `SECRET_KEY = os.environ['SECRET_KEY']`.
- **Fix:** `load_dotenv()` na samej górze `test.py`, ścieżka: `Path(__file__).resolve().parent.parent.parent.parent / '.env'`.

### 📝 Notatka: `SPECTACULAR_SETTINGS` musi mieć `COMPONENT_SPLIT_REQUEST: True`

- **Dlaczego:** Wymagane przez orval (frontend), żeby generował osobne typy `XxxRequest` (write) i `Xxx` (read) dla mutation endpointów. Bez tego write/read mają ten sam shape, co rozwala orval mutation hooks.
- **Dodatkowo zalecane:** `SERVE_INCLUDE_SCHEMA: False` — zapobiega żeby `/api/schema/` opisywał sam siebie rekurencyjnie.

### 📝 Notatka: drf-spectacular 0.29+ nie wypisuje nic przy sukcesie

- **Odkryte:** Issue #1
- **Zachowanie:** `python manage.py spectacular --validate` kończy z exit code 0 i pustym stdout gdy schema jest poprawna. NIE szukaj stringa "No issues found" — nowsze wersje są ciche.
- **Weryfikacja:** Sprawdzaj exit code, nie tekst outputu.

---

## React / Frontend

_Brak wpisów — będzie uzupełnione od issue #2._

---

## DevOps / Tooling

### ⚠️ Pułapka: Docker Compose musi jawnie przekazywać zmienne env do kontenerów

- **Odkryte:** Issue #1
- **Objaw:** Po przeniesieniu `SECRET_KEY` z hardcoded settings do `.env`, kontener crashuje przy starcie z `KeyError: 'SECRET_KEY'`.
- **Dlaczego:** Docker Compose czyta `.env` do interpolacji `${VAR}` w YAMLu, ale NIE forwarduje automatycznie wszystkich zmiennych do kontenerów. Każda zmienna potrzebna w kontenerze musi być jawnie wymieniona pod `environment:`.
- **Fix:** W `docker-compose.yml`, kontener `api` musi mieć:
```yaml

### 📝 Notatka: GitHub dzieli numerację issues + PR — nie zakładać kolejnych numerów dla issues

- **Odkryte:** Issue #6 (hotfix `timezone` import), 2026-05-07
- **Problem:** Założenie "kolejny issue dostanie numer X+1" jest błędne. PR-y zajmują numery z tej samej puli co issues. Issue planowane jako #24 w roadmapie w rzeczywistości otrzymało numer #6, bo między #1 a tym hotfixem powstało 5 PR-ów.
- **Wpływ:** `Closes #24` w body PR nie zadziałało (issue #24 nie istniał). Hotfix issue #6 musiał być zamknięty ręcznie przez `gh issue close 6`.
- **Fix:** W `PROJECT-BRIEF.md` używać symbolicznych nazw (`AUDIT-1`, `AUDIT-2`...) zamiast spekulować numery. Realny numer GitHub przyznawać przy tworzeniu issue, dopisać go obok nazwy symbolicznej w tabeli.
- **Format zapisu:** `**AUDIT-1** [hotfix] ... — created as #6, fixed via PR #7`
- **Konsekwencja dla planów:** W `docs/plans/GH-N-*.md` używać **realnego numeru GitHub** (po utworzeniu issue), nie planowanego z roadmapu.