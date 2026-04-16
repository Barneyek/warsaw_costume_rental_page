from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import NewsPost
from .serializers import NewsPostSerializer


class NewsListView(ListAPIView):
    serializer_class = NewsPostSerializer
    queryset = NewsPost.objects.filter(is_published=True)


class NewsDetailView(RetrieveAPIView):
    serializer_class = NewsPostSerializer
    lookup_field = 'slug'
    queryset = NewsPost.objects.filter(is_published=True)
