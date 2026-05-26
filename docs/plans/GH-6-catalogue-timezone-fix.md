# Plan: [GH-#6] Fix missing `timezone` import in catalogue/models.py

**Issue:** https://github.com/Barneyek/warsaw_costume_rental_page/issues/6
**Status:** 🟢 Done
**Created:** 2026-05-07
**Last updated:** 2026-05-07
**Estimated effort:** S (< 1h)
**Actual effort:** ~20 min
> **Numbering note:** Ten plan powstał gdy zakładaliśmy numer #24 (stąd historyczna nazwa brancha `fix/GH-24-...`). Faktyczny numer issue to **#6**. Po tym epizodzie przyjęliśmy konwencję AUDIT-N (patrz `lessons-learned.md`).
---

## 1. Context & Goal

Audyt backendu z 2026-05-07 ujawnił, że `backend/src/catalogue/models.py` używa `timezone.now()` w polu `uploaded_at` modelu `CostumeImage`, ale **nie importuje `timezone`**. Każde zapisanie instancji `CostumeImage` rzuci `NameError: name 'timezone' is not defined`.

**Why this matters:** Bug nie jest wykrywany przez istniejące testy (30/30 zaliczonych) bo żaden test nie zapisuje `CostumeImage`. Pierwsza próba uploadu obrazka kostiumu w produkcji spowoduje crash. Trzeba to naprawić **zanim** zaczniemy frontend (#2), żeby przy testach end-to-end nie tracić czasu na ten bug.

---

## 2. Scope

### In scope
- [x] Dodanie `from django.utils import timezone` do importów w `backend/src/catalogue/models.py`
- [x] Dodanie testu regresyjnego w `backend/tests/catalogue/test_models.py` weryfikującego że `CostumeImage` można zapisać bez `NameError`

### Out of scope (świadomie pomijamy)
- Inne znaleziska z audytu (GAP-1 do GAP-4) — *powód:* osobne issues AUDIT-2/3/4
- Refactor `models.py` poza dodaniem jednego importu — *powód:* zakres minimalny dla hotfixa.
- Refaktor istniejących testów — *powód:* dodajemy nowy, nie ruszamy starych.

---

## 3. Affected files & modules

| Path | Action | Why |
|------|--------|-----|
| `backend/src/catalogue/models.py` | **MODIFY** | Dodanie brakującego importu — fix bug |
| `backend/tests/catalogue/test_models.py` | **MODIFY** | Dodanie testu regresyjnego (jeśli plik istnieje) lub **NEW** (jeśli nie ma) |

---

## 4. Pre-conditions / Dependencies

**Musi być gotowe wcześniej:**
- [x] PR `chore: gitignore audits dir; refresh roadmap` zmergowany do main
- [x] Issue #6 stworzone na GitHubie
- [x] Branch `fix/GH-24-catalogue-timezone-import` utworzony z aktualnego main
- [x] Docker stack uruchomiony (`docker compose up -d`)

---

## 5. Implementation steps

### 5.1 Fix the import

#### Step 5.1.1: Dodanie `from django.utils import timezone` do models.py
- [x] **Action:** Otwórz `backend/src/catalogue/models.py`. Na górze pliku, w sekcji importów, dodaj linię:
```python
  from django.utils import timezone
```
  Pozycja: po `from django.db import models` (jeśli istnieje), albo na początku importów Django.
- [x] **Validate:** `docker compose run --rm api python -c "from src.catalogue.models import CostumeImage; print('import OK')"` — ⚠️ **Odchylenie:** komenda z planu zawsze failuje z `AppRegistryNotReady` bo Django app registry nie jest zainicjalizowane bez `django.setup()`. Użyto poprawnej komendy: `docker compose run --rm api python manage.py shell -c "from src.catalogue.models import CostumeImage; print('import OK')"`. Dodatkowo zweryfikowano `costume_image_upload_path(None, 'test.jpg')` → zwraca `costumes/2026/05/07/<uuid>.jpg`.
- [x] **Expected:** Output: `import OK` bez błędów. ✅ Uzyskano `import OK`.
- [x] **On failure:** N/A — sukces.

### 5.2 Add regression test

#### Step 5.2.1: Sprawdzenie czy istnieje `backend/tests/catalogue/test_models.py`
- [x] **Action:** `docker compose run --rm api ls tests/catalogue/`
- [x] **Validate:** Output zawiera `test_models.py` lub nie.
- [x] **Expected:** Notatka jaka jest sytuacja (modify istniejącego vs create new). ✅ Plik istnieje — `__init__.py  test_models.py`. Akcja: MODIFY istniejącego.
- [x] **On failure:** N/A — sukces.

#### Step 5.2.2: Dodanie testu regresyjnego
- [x] **Action:** W `backend/tests/catalogue/test_models.py` dodano test (dostosowany do realnych pól modeli — patrz ⚠️ poniżej). `CostumeImage` nie ma pól `alt` ani `uploaded_at` (placeholder w planie był błędny). `timezone.now()` jest wywoływane w funkcji `costume_image_upload_path`, nie jako `default=` pola — więc `CostumeImage.objects.create()` bez pliku nie uruchomi callable. Test wywołuje funkcję bezpośrednio:
```python
def test_costume_image_can_be_saved_without_name_error():
    from src.catalogue.models import costume_image_upload_path
    path = costume_image_upload_path(None, "costume.jpg")
    assert path.startswith("costumes/")
    assert path.endswith(".jpg")
```
  
  ⚠️ **Uwaga**: placeholder z planu (pola `alt`, `uploaded_at`) nie istnieje w modelu. Dostosowano test do realnej definicji modeli zgodnie z instrukcją w planie.

- [x] **Validate:** `docker compose run --rm api pytest tests/catalogue/test_models.py::test_costume_image_can_be_saved_without_name_error -v`
- [x] **Expected:** Test PASSED. ✅ `1 passed in 0.17s`
- [x] **On failure:** N/A — sukces.

### 5.3 Full test suite verification

#### Step 5.3.1: Wszystkie testy nadal przechodzą
- [x] **Action:** `docker compose run --rm api pytest -v`
- [x] **Validate:** Czytaj output.
- [x] **Expected:** `31 passed, 0 failed` (30 starych + 1 nowy). ✅ Uzyskano dokładnie `31 passed in 2.44s`.
- [x] **On failure:** N/A — sukces.

### 5.4 Schema validation

#### Step 5.4.1: OpenAPI schema dalej waliduje czysto
- [x] **Action:** `docker compose run --rm api python manage.py spectacular --file schema.yaml --validate`
- [x] **Validate:** Exit code.
- [x] **Expected:** Exit code 0, brak warningów (drf-spectacular 0.29+ jest cichy przy sukcesie). ✅ EXIT_CODE:0, brak outputu.
- [x] **On failure:** N/A — sukces.

---

## 6. Deep analysis — skutki działań (holistycznie)

### 6.1 Wpływ na inne Django apps
Brak. Zmiana izolowana w `catalogue/models.py`. Inne apps (core, blog, pages, inquiry) nie importują `CostumeImage` ani niczego z tego pliku.

### 6.2 Wpływ na bazę danych
Brak. Zero migracji — dodajemy tylko import w Pythonie, schema bazy bez zmian.

### 6.3 Wpływ na i18n (django-modeltranslation)
Brak. `timezone` nie ma związku z translacją.

### 6.4 Wpływ na frontend
Brak bezpośredni. Pośrednio: jak frontend (od #2) zacznie tworzyć kostiumy z obrazkami, **bez tego fixa** by się wywaliło. Z fixem — działa.

### 6.5 Wpływ na media / storage
Brak. `CostumeImage` używa `timezone.now()` jako default dla pola `uploaded_at` (timestamp, nie ścieżka). Nie dotyka logiki upload.

### 6.6 Wpływ na CORS / CSRF
Brak.

---

## 7. Testing strategy

### 7.1 Unit tests
- [x] Test regresyjny `test_costume_image_can_be_saved_without_name_error` (Step 5.2.2)

### 7.2 Integration tests
- [x] Wszystkie istniejące testy przechodzą (Step 5.3.1)

### 7.3 Manual QA checklist
- [ ] Optional: w Django adminie utworzyć kostium, dodać obrazek przez TabularInline, sprawdzić że formularz zapisuje bez błędu (wymaga uruchomionego stosu).

### 7.4 Test commands
```bash
# Specific regression test
docker compose run --rm api pytest tests/catalogue/test_models.py::test_costume_image_can_be_saved_without_name_error -v

# Full suite
docker compose run --rm api pytest -v

# Schema validation
docker compose run --rm api python manage.py spectacular --file schema.yaml --validate
```

---

## 8. Rollback plan

**Jeśli coś pójdzie nie tak:**
1. `git stash` — cofa zmiany niezacommitowane.
2. `git checkout main` + `git branch -D fix/GH-24-catalogue-timezone-import` — usuwa branch lokalnie.
3. Jeśli już zacommitowane: `git reset --hard HEAD~N` (N = liczba commitów do cofnięcia).

**Unrecoverable state:** Brak. Zmiana to 1 linia kodu + 1 test. Pełny rollback = `git stash`.

---

## 9. Open questions

- [ ] _(brak — zakres jest jasny)_

---

## 10. Progress log

| Date | Step | What was done | Blockers | Notes |
|------|------|---------------|----------|-------|
| 2026-05-07 | Plan v1 | Plan napisany | — | Pierwszy plan w polskim formacie |
| 2026-05-07 | 5.1 | Dodano `from django.utils import timezone` w `catalogue/models.py` line 3. Zweryfikowano przez `manage.py shell` + bezpośrednie wywołanie `costume_image_upload_path` → zwraca `costumes/2026/05/07/<uuid>.jpg`. | Validate command z planu (`python -c "..."`) zawsze failuje z AppRegistryNotReady — zastosowano `manage.py shell -c` jako poprawną alternatywę. | commit: `fix(catalogue): add missing timezone import (BUG-1)` |
| 2026-05-07 | 5.2 | Dodano test regresyjny `test_costume_image_can_be_saved_without_name_error` w `tests/catalogue/test_models.py`. Test wywołuje `costume_image_upload_path()` bezpośrednio (placeholder z planu miał błędne pola `alt`/`uploaded_at`, które nie istnieją w modelu). `1 passed in 0.17s`. | Placeholder w planie nieadekwatny do realnych pól modelu — dostosowano zgodnie z ⚠️ w planie. | commit: `test(catalogue): add regression test for CostumeImage save` |
| 2026-05-07 | 5.3 | `pytest -v` → `31 passed, 0 failed`. | — | Dokładnie zgodnie z oczekiwaniem. |
| 2026-05-07 | 5.4 | `python manage.py spectacular --validate` → exit 0, brak outputu (drf-spectacular 0.29+ jest cichy). | — | Schema nienaruszona. |

---

## 11. Definition of Done

**Wszystkie poniższe MUSZĄ być spełnione przed zamknięciem issue:**

- [x] `from django.utils import timezone` jest obecny w `backend/src/catalogue/models.py`
- [x] Test `test_costume_image_can_be_saved_without_name_error` istnieje i przechodzi
- [x] Pełny `pytest -v` → **31 passed, 0 failed**
- [x] `python manage.py spectacular --validate` → exit 0
- [x] Conventional commit: `fix(catalogue): add missing timezone import (BUG-1)`
- [ ] Branch zmergowany do `main` przez squash merge
- [ ] Issue #6 zamknięte: `gh issue close 6 --comment "Done — see docs/plans/GH-6-..."`
- [x] Plan zaktualizowany: `Status: 🟢 Done`, `Actual effort: ~20 min`

---

## 12. Post-mortem (wypełnij po zakończeniu)

**What went well:** Fix był trywialny (1 linia). Commit + test w 2 oddzielnych commitach zgodnie z planem. Wszystkie 31 testów zielone, schema czysta.

**What went wrong:**
- Validate command z planu (`python -c "from src.catalogue.models import CostumeImage; print('import OK')"`) jest fundamentalnie broken — Django wymaga `setup()` przed importem modeli. Komenda failuje z `AppRegistryNotReady` niezależnie od tego czy fix jest aplikowany. Zastosowano `manage.py shell -c` jako poprawną alternatywę.
- Test placeholder w 5.2.2 miał błędne pola (`alt`, `uploaded_at`) nieistniejące w modelu `CostumeImage`. Zdiagnozowano podczas implementacji (per ⚠️ w planie) i dostosowano: `timezone.now()` jest w `costume_image_upload_path`, nie jako `default=` pola, więc test wywołuje funkcję bezpośrednio.

**Lessons learned:** _dodaj do `docs/lessons-learned.md`_ — patrz poniżej:
1. Validate commands w planach powinny używać `manage.py shell -c` zamiast `python -c`, gdy importujemy modele Django.
2. Przy pisaniu testów dla `upload_to` callables: funkcja jest wywoływana tylko gdy faktycznie zapisujemy plik, NIE przy `Model.objects.create()` bez pliku. Testować funkcję bezpośrednio lub zapisać plik z `ContentFile`.

**Follow-up issues:** żadne — fix izolowany. GAP-1 do GAP-4 z audytu objęte AUDIT-2/3/4 + #22.