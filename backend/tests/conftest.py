import pytest
from src.catalogue.models import Category, Tag, Size, Costume


@pytest.fixture
def category():
    return Category.objects.create(name="Historyczne", slug="historyczne")


@pytest.fixture
def tag():
    return Tag.objects.create(name="Halloween")


@pytest.fixture
def size():
    return Size.objects.create(name="M")


@pytest.fixture
def costume(category, size, tag):
    c = Costume.objects.create(
        name="Rycerz Średniowieczny",
        slug="rycerz-sredniowieczny",
        price="150.00",
        deposit="50.00",
    )
    c.categories.add(category)
    c.sizes.add(size)
    c.tags.add(tag)
    return c
