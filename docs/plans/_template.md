# Plan: [GH-#<issue-number>] <title>

**Issue:** <URL do GH issue>
**Status:** 🟡 In Progress  <!-- 🟡 In Progress | 🟢 Done | 🔴 Blocked | ⏸️ Paused -->
**Created:** <YYYY-MM-DD>
**Last updated:** <YYYY-MM-DD>
**Estimated effort:** <S (< 1h) | M (1-4h) | L (4-8h) | XL (> 8h)>
**Actual effort:** <fill at the end>

---

## 1. Context & Goal

<Dlaczego to robimy, jaki problem rozwiązuje, jak wpisuje się w większą całość projektu>

**Why this matters:** <1-2 zdania — dlaczego bez tego nie ruszymy dalej>

---

## 2. Scope

### In scope
- [ ] ...
- [ ] ...

### Out of scope (świadomie pomijamy)
- ... — *powód:* ...
- ... — *powód:* ...

---

## 3. Affected files & modules

| Path | Action | Why |
|------|--------|-----|
| `backend/src/xxx/models.py` | NEW | Define domain models |
| `backend/src/xxx/admin.py` | MODIFY | Register new models |
| `backend/tests/xxx/test_models.py` | NEW | Model unit tests |

---

## 4. Pre-conditions / Dependencies

**Musi być gotowe wcześniej:**
- [ ] Issue #X ukończone (jeśli zależność)
- [ ] Paczka X zainstalowana
- [ ] Zmienna env Y ustawiona

**Jeśli coś z powyższego nie jest gotowe — STOP, nie zaczynaj.**

---

## 5. Implementation steps

> Każdy krok ma `action` (co robić), `validate` (jak sprawdzić że zadziałało), `expected` (co powinno się pojawić).
> Krok uznajemy za ukończony TYLKO gdy `validate` zwraca `expected`.

### 5.1 <Sekcja 1 — np. Models>

#### Step 5.1.1: <short action>
- [ ] **Action:** <co zrobić, konkretnie — plik, funkcja, linia>
- [ ] **Validate:** <komenda / sprawdzenie>
- [ ] **Expected:** <co powinno być outputem / co zobaczysz>
- [ ] **On failure:** <co zrobić jeśli nie zadziałało>

#### Step 5.1.2: ...

### 5.2 <Sekcja 2 — np. Migrations>

#### Step 5.2.1: Create migration
- [ ] **Action:** `python manage.py makemigrations catalogue`
- [ ] **Validate:** Check file `backend/src/catalogue/migrations/0001_initial.py` exists
- [ ] **Expected:** Output like `Migrations for 'catalogue': 0001_initial.py - Create model Costume, Create model Category`
- [ ] **On failure:** Check `INSTALLED_APPS`, check model syntax

#### Step 5.2.2: Apply migration
- [ ] **Action:** `python manage.py migrate`
- [ ] **Validate:** `python manage.py showmigrations catalogue`
- [ ] **Expected:** `[X] 0001_initial`
- [ ] **On failure:** Check DB connection, check migration file for syntax issues

### 5.3 <Tests>

#### Step 5.3.1: ...

---

## 6. Deep analysis — skutki działań (holistycznie)

### 6.1 Wpływ na inne Django apps
- `app X` — <czy coś się zmienia, czy są breaking changes>
- `app Y` — ...

### 6.2 Wpływ na bazę danych
- Nowe tabele: ...
- Nowe indeksy: ...
- Migracje odwracalne? Tak / Nie (jeśli Nie — uzasadnić)

### 6.3 Wpływ na i18n (django-modeltranslation)
- Które pola tłumaczone: ...
- Wymaga regeneracji migracji po dodaniu tłumaczeń? Tak / Nie

### 6.4 Wpływ na frontend
- Zod schemas do aktualizacji: `src/types/...`
- Nowe typy TS (via `z.infer<>`): ...
- Breaking API changes: ...

### 6.5 Wpływ na media / storage
- Nowe foldery `media/`: ...
- Upload paths: ...

### 6.6 Wpływ na CORS / CSRF
- Nowe endpointy: ...
- Zmiany w `CORS_ALLOWED_ORIGINS`: ...

---

## 7. Testing strategy

### 7.1 Unit tests (pytest-django)
- [ ] Test model creation z poprawnymi danymi
- [ ] Test validation errors (required fields)
- [ ] Test M2M relations
- [ ] Test custom methods/properties

### 7.2 Integration tests
- [ ] Admin works (create/edit/delete via admin)
- [ ] API endpoint returns correct data
- [ ] Filtering works

### 7.3 Manual QA checklist
- [ ] <scenariusz użytkownika 1>
- [ ] <scenariusz użytkownika 2>

### 7.4 Test commands
```powershell
# Run all tests for this module
cd backend
pytest tests/<app>/ -v

# Run with coverage
pytest tests/<app>/ --cov=src.<app> --cov-report=term-missing
```

---

## 8. Rollback plan

**Jeśli coś pójdzie nie tak:**
1. `git stash` lub `git reset --hard HEAD~1`
2. `python manage.py migrate <app> <previous_migration>` — cofnięcie migracji
3. Usunąć: <lista plików>

**Unrecoverable state:** <co NIE da się cofnąć i wymaga restore z backupu>

---

## 9. Open questions

- [ ] <pytanie, na które potrzebujemy odpowiedzi zanim zamkniemy>
- [ ] ...

---

## 10. Progress log

| Date | Step | What was done | Blockers | Notes |
|------|------|---------------|----------|-------|
| YYYY-MM-DD | 5.1.1 | Category model defined | — | Used CharField(200) |
| YYYY-MM-DD | 5.2.1 | ❌ Migration failed | Missing app in INSTALLED_APPS | Fixed, retried |

---

## 11. Definition of Done

**Wszystkie poniższe MUSZĄ być spełnione żeby zamknąć issue:**

- [ ] Wszystkie kroki z sekcji 5 odhaczone (`[x]`)
- [ ] Wszystkie walidacje zwróciły `expected`
- [ ] Testy z sekcji 7 przechodzą (0 fail)
- [ ] Manual QA wszystkie scenariusze OK
- [ ] Code review (self) — zero `TODO`, zero `print()`, zero zakomentowanego kodu
- [ ] Commity z conventional commits (`feat:`, `fix:`, `test:`)
- [ ] Push na `main`
- [ ] Issue closed via `gh issue close <N> --comment "Done — see docs/plans/GH-<N>-*.md"`
- [ ] Plan zaktualizowany: `Status: 🟢 Done`, `Actual effort: X`

---

## 12. Post-mortem (wypełnij po zakończeniu)

**What went well:** <dobra decyzja, oszczędziło czas>
**What went wrong:** <błąd/blocker, stracony czas>
**Lessons learned:** <do `docs/lessons-learned.md`>
**Follow-up issues:** <czy odkryliśmy coś co wymaga osobnego issue>