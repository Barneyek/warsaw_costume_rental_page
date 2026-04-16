from django.contrib import admin
from .models import SiteSettings, GlobalAlert


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(GlobalAlert)
class GlobalAlertAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('is_active',)
