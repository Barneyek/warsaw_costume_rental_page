from django.urls import path
from .views import InquirySubmitView

urlpatterns = [
    path('inquiry/submit/', InquirySubmitView.as_view(), name='inquiry-submit'),
]
