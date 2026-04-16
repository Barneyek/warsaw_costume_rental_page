from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Costume, Category
from .serializers import CostumeListSerializer, CostumeDetailSerializer, CategorySerializer
from .filters import CostumeFilter


class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CostumeListView(ListAPIView):
    serializer_class = CostumeListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CostumeFilter

    def get_queryset(self):
        return (
            Costume.objects
            .filter(is_active=True)
            .prefetch_related('categories', 'images', 'tags', 'sizes')
        )


class CostumeDetailView(RetrieveAPIView):
    serializer_class = CostumeDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Costume.objects
            .filter(is_active=True)
            .prefetch_related('categories', 'images', 'tags', 'sizes')
        )
