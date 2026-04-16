import uuid
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent_category = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )

    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tagi'

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = 'Rozmiar'
        verbose_name_plural = 'Rozmiary'

    def __str__(self):
        return self.name


def costume_image_upload_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1]
    today = timezone.now()
    return f'costumes/{today:%Y/%m/%d}/{uuid.uuid4()}.{ext}'


class Costume(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='costumes')
    tags = models.ManyToManyField(Tag, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)

    class Meta:
        verbose_name = 'Kostium'
        verbose_name_plural = 'Kostiumy'

    def __str__(self):
        return self.name


class CostumeImage(models.Model):
    costume = models.ForeignKey(Costume, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=costume_image_upload_path)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Zdjęcie kostiumu'
        verbose_name_plural = 'Zdjęcia kostiumów'

    def __str__(self):
        return f'Zdjęcie – {self.costume.name}'
