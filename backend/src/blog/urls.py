from django.urls import path
from .views import NewsListView, NewsDetailView

urlpatterns = [
    path('news/', NewsListView.as_view(), name='news-list'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news-detail'),
]
