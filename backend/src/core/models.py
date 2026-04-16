from django.db import models


class SiteSettings(models.Model):
    """Singleton – globalna konfiguracja strony."""
    site_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Ustawienia strony'
        verbose_name_plural = 'Ustawienia strony'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name


class GlobalAlert(models.Model):
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    class Meta:
        verbose_name = 'Komunikat globalny'
        verbose_name_plural = 'Komunikaty globalne'

    def __str__(self):
        return self.message[:60]
