import django_filters
from .models import Costume


class CostumeFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='categories__id')
    category_slug = django_filters.CharFilter(field_name='categories__slug')
    tag = django_filters.NumberFilter(field_name='tags__id')
    size = django_filters.NumberFilter(field_name='sizes__id')

    class Meta:
        model = Costume
        fields = ['category', 'category_slug', 'tag', 'size', 'is_available']
