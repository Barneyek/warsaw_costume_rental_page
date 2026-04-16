from django.urls import path
from .views import InitView

urlpatterns = [
    path('init/', InitView.as_view(), name='init'),
]
