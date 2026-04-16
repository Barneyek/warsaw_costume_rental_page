from rest_framework import serializers
from .models import SiteSettings, GlobalAlert


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'contact_email', 'facebook_url', 'instagram_url']


class GlobalAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalAlert
        fields = ['id', 'message', 'valid_from', 'valid_until']
