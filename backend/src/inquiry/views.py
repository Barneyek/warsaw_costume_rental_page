from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inquiry
from .serializers import InquirySubmitSerializer


class InquirySubmitView(CreateAPIView):
    serializer_class = InquirySubmitSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()
        return Response({'status': 'ok', 'id': inquiry.pk}, status=status.HTTP_201_CREATED)
