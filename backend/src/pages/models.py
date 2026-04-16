from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(help_text='Obsługuje Markdown')

    class Meta:
        verbose_name = 'Strona'
        verbose_name_plural = 'Strony'

    def __str__(self):
        return self.title
