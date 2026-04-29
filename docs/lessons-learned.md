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
| GitHub Issues (title + body) | EN |
| `docs/plans/GH-N-*.md` | EN | Generowane przez Claude Code |
| **`docs/lessons-learned.md`** | **PL** | Notatki dla siebie — myślę po polsku |
| `CLAUDE.md` | EN | Konsumowane przez AI |

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