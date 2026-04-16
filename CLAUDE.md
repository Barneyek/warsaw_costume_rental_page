# Projekt: Warsaw Costume Rental (Django + React)

**Cel:** Budowa skalowalnej aplikacji typu decoupled (Headless CMS) w celach edukacyjnych. Skupienie na czystej architekturze danych, asynchronicznej komunikacji i nowoczesnym UX.

## 🏗️ Architektura Backend (Django + DRF)

### 1. core (Klej systemowy)

- **Zadanie:** Globalna konfiguracja i "handshake" z Reactem.
- **Modele:** * `SiteSettings` (Singleton): Sociale, kontakt, globalny email.
    - `GlobalAlert`: System komunikatów z polami valid_from i valid_until (automatyczny harmonogram wyświetlania) oraz is_active.
- **API:** `/api/init/` – zwraca konfigurację strony przy starcie aplikacji frontendowej.

### 2. catalogue (Serce systemu)

- **Modele:**
    - `Category` (name, slug, parent_category).
    - `Tag` (proste etykiety, np. "Halloween").
    - `Size` (predefiniowana lista rozmiarów).
    - `Costume`
        - Pola: name, description, slug, price, deposit, is_active, is_available.
        - Relacje: `category` (FK), `tags` (M2M), **`sizes` (M2M)**.
    - `CostumeImage`: Relacja 1: N do Costume.
- **Media & Optymalizacja:** * Upload z UUID do folderów `costumes/%Y/%m/%d/`.
    - Integracja z **Pillow / django-imagekit** – automatyczne generowanie lekkich miniatur (thumbnails) dla listy produktów.
- **API:** `/api/costumes/` z obsługą `django-filter` (filtrowanie po kategorii, rozmiarze, tagu) oraz **paginacją** (PageNumberPagination).

### 3. blog & pages (Content)

- **blog:** Proste newsy/aktualności na stronę główną (`/api/news/`).
- **pages:** Płaskie strony informacyjne (O nas, Regulamin). Pole `content` obsługuje **Markdown**, który React renderuje przez `react-markdown`.

### 4. inquiry (System zapytań)

- **Model w bazie:** `Inquiry` (customer_name, customer_email, message, status [new/read/replied], created_at).
- **Relacja:** `items` (M2M do Costume) – aby wiedzieć, o jakie stroje pytał klient.
- **Logic:** Endpoint `/api/inquiry/submit/` zapisuje dane w bazie, a następnie `services.py` wysyła powiadomienia e-mail.

---

## 💻 Frontend (React + Vite)

- **Zarządzanie Stanem:** `Context API` + `localStorage` do obsługi schowka (wybrane stroje nie znikają po odświeżeniu strony).
- **i18n:** Backend wysyła oba języki (np. `name_pl`, `name_en`), a React na podstawie swojego stanu decyduje, który klucz wyświetlić.
- **Routing:** `react-router-dom` do nawigacji między katalogiem, newsami i podstronami.

---

## 🛠️ Checklist Techniczny

1. **CORS:** Konfiguracja `django-cors-headers` (zezwolenie na port Reacta).
2. **i18n:** Implementacja `django-modeltranslation` dla modeli w bazie.
3. **Admin:** Konfiguracja `TabularInline` dla zdjęć filter_horizontal dla rozmiarów i tagów, obsługa statusów zapytań.
4. **Serializers:** Logika mapowania języków i serwowania URL-i do m

## **📅 Kolejność Implementacji**

1. Setup środowiska ← .env, requirements, struktura projektu, Git
2. Django Models ← jak masz
3. Django Admin ← jak masz
4. API (DRF) ← jak masz + przynajmniej kilka testów pytest-django
5. React ← jak masz
6. (opcjonalnie) Docker Compose ← db + backend + frontend w jednej komendzie