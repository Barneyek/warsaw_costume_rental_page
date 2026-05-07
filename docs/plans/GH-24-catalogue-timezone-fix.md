# Plan: [GH-#24] Fix missing `timezone` import in catalogue/models.py

**Issue:** https://github.com/Barneyek/warsaw_costume_rental_page/issues/24
**Status:** 🟡 In Progress
**Created:** 2026-05-07
**Last updated:** 2026-05-07
**Estimated effort:** S (< 1h)
**Actual effort:** _wypełnij na końcu_

---

## 1. Context & Goal

Audyt backendu z 2026-05-07 ujawnił, że `backend/src/catalogue/models.py` używa `timezone.now()` w polu `uploaded_at` modelu `CostumeImage`, ale **nie importuje `timezone`**. Każde zapisanie instancji `CostumeImage` rzuci `NameError: name 'timezone' is not defined`.

**Why this matters:** Bug nie jest wykrywany przez istniejące testy (30/30 zaliczonych) bo żaden test nie zapisuje `CostumeImage`. Pierwsza próba uploadu obrazka kostiumu w produkcji spowoduje crash. Trzeba to naprawić **zanim** zaczniemy frontend (#2), żeby przy testach end-to-end nie tracić czasu na ten bug.

---

## 2. Scope

### In scope
- [ ] Dodanie `from django.utils import timezone` do importów w `backend/src/catalogue/models.py`
- [ ] Dodanie testu regresyjnego w `backend/tests/catalogue/test_models.py` weryfikującego że `CostumeImage` można zapisać bez `NameError`

### Out of scope (świadomie pomijamy)
- Inne znaleziska z audytu (GAP-1 do GAP-4) — *powód:* osobne issues #25-#27.
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
- [x] Issue #24 stworzone na GitHubie
- [x] Branch `fix/GH-24-catalogue-timezone-import` utworzony z aktualnego main
- [x] Docker stack uruchomiony (`docker compose up -d`)

---

## 5. Implementation steps

### 5.1 Fix the import

#### Step 5.1.1: Dodanie `from django.utils import timezone` do models.py
- [ ] **Action:** Otwórz `backend/src/catalogue/models.py`. Na górze pliku, w sekcji importów, dodaj linię:
```python