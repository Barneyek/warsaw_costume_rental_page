from django.urls import path
from .views import CategoryListView, CostumeListView, CostumeDetailView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('costumes/', CostumeListView.as_view(), name='costume-list'),
    path('costumes/<slug:slug>/', CostumeDetailView.as_view(), name='costume-detail'),
]
