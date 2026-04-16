from django.db import models


class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Aktualność'
        verbose_name_plural = 'Aktualności'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
