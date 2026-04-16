# Notatki z nauki Django + DRF
> Projekt: Warsaw Costume Rental | Stack: Django + DRF (backend), React + Vite + TS (frontend)

---

## 1. Struktura projektu Django

Django dzieli się na dwa poziomy:

- **Projekt** — jeden byt, jedna baza danych, globalna konfiguracja (settings, urls, wsgi)
- **App** — moduł wewnątrz projektu odpowiedzialny za jedną domenę biznesową

Appy tworzy się komendą:
```bash
python manage.py startapp nazwa_appu
```

Każdy app ma swoje własne pliki: `models.py`, `admin.py`, `views.py`, `serializers.py`, `urls.py`.

### Nasza struktura (Opcja B — pełne ścieżki importów)
```
warsaw_costume_rental/          ← root repozytorium
├── backend/
│   ├── src/                    ← wszystkie Django apps
│   │   ├── blog/               ← aktualności
│   │   ├── catalogue/          ← kostiumy, kategorie, tagi
│   │   ├── core/               ← ustawienia strony, alerty
│   │   ├── inquiry/            ← zapytania klientów
│   │   └── pages/              ← strony statyczne
│   ├── tests/
│   ├── web_app/                ← konfiguracja Django
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   └── dev.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docker-compose.yml
└── .env
```

Opcja B oznacza że wszędzie używamy pełnych ścieżek:
```python
# INSTALLED_APPS
'src.blog',
'src.catalogue',

# Importy cross-app
from src.catalogue.models import Costume
```

---

## 2. INSTALLED_APPS — co to jest?

Lista w `settings.py` która mówi Django: *"te moduły istnieją, używaj ich"*. Bez wpisania appu Django go dosłownie nie widzi — nie zrobi migracji, nie pokaże w adminie.

```python
INSTALLED_APPS = [
    # Domyślne Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Biblioteki zewnętrzne (third-party)
    'rest_framework',       # DRF — API
    'corsheaders',          # CORS — komunikacja z Reactem
    'django_filters',       # filtrowanie w API

    # Nasze appy
    'src.core',
    'src.catalogue',
    'src.blog',
    'src.pages',
    'src.inquiry',
]
```

---

## 3. Modele (`models.py`) — tabele w bazie danych

Klasa = tabela w bazie. Każde pole klasy = kolumna tabeli.

```python
from django.db import models

class Costume(models.Model):
    name        = models.CharField(max_length=200)       # tekst o max długości
    description = models.TextField(blank=True)           # długi tekst, może być pusty
    price       = models.DecimalField(max_digits=8, decimal_places=2)  # cena
    is_active   = models.BooleanField(default=True)      # true/false
    created_at  = models.DateTimeField(auto_now_add=True) # data, auto przy tworzeniu

    # Relacje
    categories  = models.ManyToManyField(Category, blank=True)  # wiele-do-wielu
    images      = ...  # relacja odwrotna przez related_name
```

### Typy relacji

**ForeignKey (jeden-do-wielu)** — np. zdjęcie należy do jednego kostiumu, kostium ma wiele zdjęć:
```python
class CostumeImage(models.Model):
    costume = models.ForeignKey(Costume, on_delete=models.CASCADE, related_name='images')
```
`on_delete=CASCADE` — gdy usuniesz kostium, usuną się też jego zdjęcia.
`related_name='images'` — pozwala pisać `costume.images.all()` zamiast `costume.costumeimage_set.all()`.

**ManyToManyField (wiele-do-wielu)** — np. kostium może mieć wiele kategorii, kategoria może mieć wiele kostiumów:
```python
categories = models.ManyToManyField(Category, blank=True)
```
Django automatycznie tworzy tabelę pośrednią w bazie.

### Wzorzec Singleton

Rekord który może istnieć tylko raz (np. `SiteSettings`). Wymuszony przez nadpisanie metody `save()`:
```python
class SiteSettings(models.Model):
    def save(self, *args, **kwargs):
        self.pk = 1  # zawsze zapisuje pod tym samym ID
        super().save(*args, **kwargs)
```
W adminie blokuje przycisk "Add" gdy rekord już istnieje:
```python
def has_add_permission(self, request):
    return not SiteSettings.objects.exists()
```

### Zapis `__` (podwójny underscore)

Sposób Django na "przejdź przez relację":
```python
category_slug = django_filters.CharFilter(field_name='categories__slug')
# czyli: idź do powiązanej kategorii i filtruj po jej polu slug
```

### Klasa Meta

Metadane modelu — jak ma się zachowywać:
```python
class Meta:
    verbose_name = 'Kostium'             # nazwa w adminie (liczba pojedyncza)
    verbose_name_plural = 'Kostiumy'     # nazwa w adminie (liczba mnoga)
    ordering = ['-created_at']           # domyślne sortowanie (- = malejąco)
```

### `__str__`

Co wyświetla się jako "nazwa" obiektu w adminie i terminalu:
```python
def __str__(self):
    return self.name  # zamiast "Costume object (1)"
```

---

## 4. Migracje — zapisywanie modeli do bazy

Dwuetapowy proces:

```bash
# 1. Czyta modele → tworzy pliki migracji (przepisy na tabele)
python manage.py makemigrations

# 2. Wykonuje przepisy → fizycznie tworzy tabele w PostgreSQL
python manage.py migrate
```

**Analogia:** `makemigrations` = architekt rysuje plan. `migrate` = ekipa budowlana go realizuje.

Każda zmiana w `models.py` = nowe `makemigrations` + `migrate`.

---

## 5. Admin (`admin.py`) — panel zarządzania danymi

Panel pod `/admin/` do zarządzania rekordami w bazie bez pisania SQL.

```python
from django.contrib import admin
from .models import Costume, CostumeImage

# Inline — zdjęcia dodajesz bezpośrednio przy edycji kostiumu
class CostumeImageInline(admin.TabularInline):
    model = CostumeImage
    extra = 1  # ile pustych formularzy pokazuje się domyślnie

@admin.register(Costume)
class CostumeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'price', 'is_active')   # kolumny na liście
    list_filter   = ('is_active', 'is_available')     # filtry po prawej stronie
    prepopulated_fields = {'slug': ('name',)}         # slug auto-wypełnia się z nazwy
    filter_horizontal   = ('tags', 'sizes')           # wygodny wybór M2M (dwa okna)
    inlines = [CostumeImageInline]                    # zdjęcia w tym samym formularzu
```

Dekorator `@admin.register(Model)` rejestruje model w panelu admina.

---

## 6. DRF — Django REST Framework

Biblioteka którą instalujesz do Django (`djangorestframework` w requirements.txt). Django domyślnie zwraca HTML (strony WWW). DRF sprawia że Django zwraca **JSON** — czyli dane dla Reacta.

DRF dostarcza:
- **Serializery** — tłumaczenie Python ↔ JSON
- **Gotowe klasy widoków** — obsługa GET, POST itd.
- **Filtrowanie i paginację**
- **Swagger** — automatyczna dokumentacja API

**Analogia:** Django to silnik. DRF to skrzynia biegów którą dokładasz żeby Django działało jako API.

---

## 7. Serializery (`serializers.py`) — tłumacz Python ↔ JSON

```
Obiekt Python → Serializer → JSON (dla Reacta)
JSON od Reacta → Serializer → Obiekt Python → baza danych
```

```python
from rest_framework import serializers
from .models import Costume

class CostumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costume
        fields = ['id', 'name', 'slug', 'price']  # tylko te pola wędrują do JSON
```

`ModelSerializer` = "bazuj na tym modelu, nie pisz wszystkiego od zera".

### Zagnieżdżony serializer

Zamiast `"category_id": 3` (nic nie mówi), zwraca pełny obiekt:
```python
class CostumeListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)  # many=True bo M2M = lista
```
Wynik w JSON:
```json
{
  "categories": [
    {"id": 3, "name": "Halloween", "slug": "halloween"}
  ]
}
```

### SerializerMethodField

Gdy potrzebujesz własnej logiki której DRF nie ogarnie automatycznie:
```python
class CostumeImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # deklaracja: "to pole liczę sam"

    def get_image_url(self, obj):                    # implementacja: "a oto jak"
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)
```
Konwencja: metoda musi się nazywać `get_` + nazwa pola.

### Dwa serializery dla jednego modelu

Wzorzec optymalizacyjny:
```python
# Lekki — do listy (200 kostiumów naraz, nie ładujemy wszystkiego)
class CostumeListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'slug', 'price', 'main_image']

# Pełny — do strony szczegółów jednego kostiumu
class CostumeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'slug', 'description', 'price',
                  'categories', 'tags', 'sizes', 'images']
```

---

## 8. Filtry (`filters.py`) — filtrowanie wyników API

Osobny plik z logiką filtrowania. Daje Reactowi możliwość zapytania:
```
GET /api/costumes/?category_slug=halloween&size=1
```

```python
import django_filters
from .models import Costume

class CostumeFilter(django_filters.FilterSet):
    category_slug = django_filters.CharFilter(field_name='categories__slug')
    tag           = django_filters.NumberFilter(field_name='tags__id')
    size          = django_filters.NumberFilter(field_name='sizes__id')

    class Meta:
        model  = Costume
        fields = ['category_slug', 'tag', 'size', 'is_available']
```

`field_name='categories__slug'` — zapis `__` = "przejdź przez relację i filtruj po tym polu".

---

## 9. Widoki (`views.py`) — obsługa requestów

Widok przyjmuje request od Reacta, pobiera dane z bazy przez serializer i odsyła JSON.

```
React → GET /api/costumes/ → View → Serializer → baza danych → JSON → React
```

DRF daje gotowe klasy widoków:

| Klasa | Do czego |
|---|---|
| `ListAPIView` | GET → lista obiektów |
| `RetrieveAPIView` | GET → jeden obiekt (po slug/id) |
| `CreateAPIView` | POST → zapisz nowy obiekt |
| `ListCreateAPIView` | GET lista + POST |
| `APIView` | surowy widok, piszesz wszystko ręcznie |

```python
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Costume
from .serializers import CostumeListSerializer, CostumeDetailSerializer
from .filters import CostumeFilter

class CostumeListView(ListAPIView):
    serializer_class = CostumeListSerializer
    filter_backends  = [DjangoFilterBackend]  # włącza filtrowanie przez django-filter
    filterset_class  = CostumeFilter

    def get_queryset(self):
        return (
            Costume.objects
            .filter(is_active=True)
            .select_related(...)       # optymalizacja dla ForeignKey
            .prefetch_related('categories', 'tags', 'sizes', 'images')  # optymalizacja dla M2M
        )

class CostumeDetailView(RetrieveAPIView):
    serializer_class = CostumeDetailSerializer
    lookup_field     = 'slug'  # szuka po slug zamiast domyślnego id
    ...
```

### `filter_backends` — co to jest?

Wtyczka do filtrowania. Bez niej DRF nie wie jak interpretować parametry z URL (`?category_slug=...`).
```python
filter_backends = [DjangoFilterBackend]
# Można łączyć:
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
# DjangoFilterBackend → filtrowanie (?category_slug=halloween)
# SearchFilter        → wyszukiwarka (?search=batman)
# OrderingFilter      → sortowanie (?ordering=price)
```

### Optymalizacja bazy (problem N+1)

Bez optymalizacji Django robi osobne zapytanie SQL dla każdego rekordu (np. 200 kostiumów = 200 zapytań o kategorie).

```python
.select_related('category')          # dla ForeignKey (jeden obiekt)
.prefetch_related('categories', 'tags')  # dla ManyToMany (wiele obiektów)
```
Z optymalizacją = 1-2 zapytania zamiast setek.

### Widok POST (formularz od klienta)

```python
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response

class InquirySubmitView(CreateAPIView):
    serializer_class = InquirySubmitSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # błąd? DRF sam zwraca 400
        inquiry = serializer.save()
        return Response({'status': 'ok', 'id': inquiry.pk}, status=status.HTTP_201_CREATED)
```

---

## 10. URL-e (`urls.py`) — mapa adresów

Dwupoziomowy system:

**W appie** (`catalogue/urls.py`):
```python
from django.urls import path
from .views import CostumeListView, CostumeDetailView

urlpatterns = [
    path('costumes/', CostumeListView.as_view(), name='costume-list'),
    path('costumes/<slug:slug>/', CostumeDetailView.as_view(), name='costume-detail'),
]
```

**Główny router** (`web_app/urls.py`):
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('src.catalogue.urls')),  # wszystko dostaje przedrostek /api/
    path('api/', include('src.core.urls')),
    # ...
]
```

Wynik:
```
catalogue/urls.py:  costumes/
główny urls.py:     api/
                    ─────────
wynik:              /api/costumes/
```

### `<slug:slug>` — parametr dynamiczny

```python
path('costumes/<slug:slug>/', ...)
# /api/costumes/batman-deluxe/ → slug = "batman-deluxe"
```
`slug:` = typ (tylko litery, cyfry, myślniki). `slug` = nazwa zmiennej którą dostaje View.

### `.as_view()`

Klasy widoków trzeba zamienić na funkcje które Django rozumie. `.as_view()` robi to automatycznie.

---

## 11. Przepływ danych — cały obraz

```
React: GET /api/costumes/?category_slug=halloween
              ↓
         web_app/urls.py → CostumeListView
              ↓
         filter_backends → CostumeFilter filtruje queryset
              ↓
         get_queryset() → pobiera z bazy tylko aktywne kostiumy
              ↓
         CostumeListSerializer → pakuje do JSON
              ↓
         React dostaje listę kostiumów

React: POST /api/inquiry/submit/ + dane formularza
              ↓
         InquirySubmitView.create()
              ↓
         serializer.is_valid() → walidacja danych
              ↓
         serializer.save() → zapis do bazy
              ↓
         Response({'status': 'ok'})
```

---

## 12. CORS — dlaczego React nie może gadać z Django bez tego

Gdy React działa na `localhost:5173` i pyta API na `localhost:8000`, przeglądarka domyślnie **blokuje** takie zapytanie (różne "originy" = różne porty).

`django-cors-headers` mówi Django żeby dodawało nagłówek zezwalający na takie zapytania.

```python
# settings.py
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUSI być pierwsza!
    ...
]

# Na czas developmentu:
CORS_ALLOW_ALL_ORIGINS = True
# Na produkcji zawęzisz do konkretnego URL Reacta
```

---

## 13. Management commands — własne komendy do manage.py

Skrypty które możesz odpalać przez `python manage.py nazwa_komendy`. Przydatne do seedowania bazy danymi testowymi.

Struktura plików:
```
src/catalogue/
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── seed.py
```

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Wypełnia bazę testowymi danymi'

    def handle(self, *args, **kwargs):
        # Twój kod tutaj
        self.stdout.write(self.style.SUCCESS('Gotowe!'))  # zielony tekst w terminalu
```

Odpalenie:
```bash
docker compose exec web python manage.py seed
```

---

## Słowniczek

| Pojęcie | Co oznacza |
|---|---|
| **App** | Moduł wewnątrz projektu Django (blog, catalogue...) |
| **Migration** | Plik opisujący zmiany w strukturze bazy danych |
| **Queryset** | Zestaw rekordów z bazy, można go filtrować i sortować |
| **Singleton** | Obiekt/rekord który może istnieć tylko raz |
| **Serializer** | Tłumacz między Pythonem a JSONem |
| **Endpoint** | Konkretny adres URL w API (np. `/api/costumes/`) |
| **N+1 problem** | Sytuacja gdzie Django robi osobne zapytanie SQL dla każdego rekordu |
| **CORS** | Mechanizm bezpieczeństwa przeglądarki blokujący requesty między różnymi portami |
| **DRF** | Django REST Framework — biblioteka do budowania API |
| **slug** | Czytelny URL przyjazny dla ludzi (np. `batman-deluxe` zamiast `42`) |