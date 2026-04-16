from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import SiteSettings, GlobalAlert
from .serializers import SiteSettingsSerializer, GlobalAlertSerializer


class InitView(APIView):
    """Endpoint startowy — zwraca konfigurację strony i aktywne alerty."""

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
