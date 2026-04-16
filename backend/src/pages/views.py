from rest_framework.generics import RetrieveAPIView
from .models import Page
from .serializers import PageSerializer


class PageDetailView(RetrieveAPIView):
    serializer_class = PageSerializer
    lookup_field = 'slug'
    queryset = Page.objects.all()
