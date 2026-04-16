from django.db import models
from src.catalogue.models import Costume


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nowe'),
        ('read', 'Przeczytane'),
        ('replied', 'Odpowiedziano'),
    ]

    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(Costume, blank=True, related_name='inquiries')

    class Meta:
        verbose_name = 'Zapytanie'
        verbose_name_plural = 'Zapytania'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer_name} – {self.created_at:%Y-%m-%d}'
