from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .models import SiteSettings, GlobalAlert
from .serializers import SiteSettingsSerializer, GlobalAlertSerializer


class InitView(APIView):
    """Endpoint startowy — zwraca konfigurację strony i aktywne alerty."""

    @extend_schema(
        responses=inline_serializer(
            name='InitResponse',
            fields={
                'site': SiteSettingsSerializer(),
                'alerts': GlobalAlertSerializer(many=True),
            }
        )
    )
    def get(self, request):
        settings = SiteSettings.objects.first()
        now = timezone.now()
        alerts = GlobalAlert.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now,
        )

        return Response({
            'site': SiteSettingsSerializer(settings).data if settings else {},
            'alerts': GlobalAlertSerializer(alerts, many=True).data,
        })
