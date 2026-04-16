import pytest
from django.db import IntegrityError
from src.catalogue.models import Category, Tag, Size, Costume


# ──────────────────────────────────────────────
# MARKER: @pytest.mark.django_db
# Każdy test który dotyka bazy MUSI mieć ten dekorator.
# Bez niego pytest-django zablokuje dostęp do bazy (celowo,
# żeby przypadkowo nie uruchomić ciężkich testów bez wiedzy).
# ──────────────────────────────────────────────


class TestCategoryModel:

    @pytest.mark.django_db
    def test_str_returns_name(self, category):
        # Sprawdzamy czy __str__ zwraca to czego oczekujemy.
        # Fixture 'category' pochodzi z conftest.py – pytest wstrzykuje ją automatycznie.
        assert str(category) == "Historyczne"

    @pytest.mark.django_db
    def test_slug_must_be_unique(self, category):
        # Próbujemy stworzyć drugą kategorię z tym samym slugiem.
        # SlugField(unique=True) powinno rzucić IntegrityError na poziomie bazy.
        # 'with pytest.raises(...)' mówi: "oczekuję że ten blok rzuci wyjątek".
        # Jeśli NIE rzuci – test FAILS. To jest asercja na wyjątek.
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Duplikat", slug="historyczne")

    @pytest.mark.django_db
    def test_parent_child_relationship(self):
        # Tworzymy relację parent → child bezpośrednio w teście,
        # bo to specyficzna sytuacja nie pasująca do fixture ogólnej.
        parent = Category.objects.create(name="Kostiumy", slug="kostiumy")
        child = Category.objects.create(
            name="Historyczne",
            slug="historyczne",
            parent_category=parent,
        )

        # Sprawdzamy relację w obie strony:
        assert child.parent_category == parent          # dziecko zna rodzica
        assert child in parent.children.all()           # rodzic zna dzieci (related_name='children')

    @pytest.mark.django_db
    def test_category_without_parent_is_valid(self):
        # parent_category jest nullable (null=True, blank=True).
        # Upewniamy się, że kategoria bez rodzica poprawnie się zapisuje.
        cat = Category.objects.create(name="Samodzielna", slug="samodzielna")
        assert cat.parent_category is None


class TestTagModel:

    @pytest.mark.django_db
    def test_str_returns_name(self, tag):
        assert str(tag) == "Halloween"

    @pytest.mark.django_db
    def test_name_must_be_unique(self, tag):
        # Tag(name, unique=True) – duplikat powinien rzucić IntegrityError.
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Halloween")


class TestSizeModel:

    @pytest.mark.django_db
    def test_str_returns_name(self, size):
        assert str(size) == "M"


class TestCostumeModel:

    @pytest.mark.django_db
    def test_str_returns_name(self, costume):
        assert str(costume) == "Rycerz Średniowieczny"

    @pytest.mark.django_db
    def test_default_flags(self, costume):
        # Upewniamy się że domyślne wartości pól BooleanField są zgodne z modelem.
        # Gdyby ktoś zmienił default= w modelu – ten test natychmiast to wykryje.
        assert costume.is_active is True
        assert costume.is_available is True

    @pytest.mark.django_db
    def test_m2m_category_assigned(self, costume, category):
        # Sprawdzamy że relacja M2M z kategorią działa.
        # .all() zwraca QuerySet – porównujemy przez 'in'.
        assert category in costume.categories.all()

    @pytest.mark.django_db
    def test_m2m_size_assigned(self, costume, size):
        assert size in costume.sizes.all()

    @pytest.mark.django_db
    def test_m2m_tag_assigned(self, costume, tag):
        assert tag in costume.tags.all()

    @pytest.mark.django_db
    def test_slug_must_be_unique(self, costume):
        with pytest.raises(IntegrityError):
            Costume.objects.create(
                name="Inny kostium",
                slug="rycerz-sredniowieczny",  # ten slug już istnieje
                price="100.00",
            )

    @pytest.mark.django_db
    def test_deposit_defaults_to_zero(self):
        # Tworzymy kostium BEZ podawania deposit – powinno wziąć default=0.
        costume = Costume.objects.create(
            name="Prosty kostium",
            slug="prosty-kostium",
            price="80.00",
        )
        assert costume.deposit == 0
