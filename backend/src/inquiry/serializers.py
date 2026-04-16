from rest_framework import serializers
from .models import Inquiry


class InquirySubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['customer_name', 'customer_email', 'message', 'items']
