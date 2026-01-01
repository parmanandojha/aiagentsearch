"""
URLs for discovery_app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history, name='history'),
    path('api/search/stream', views.api_search_stream, name='api_search_stream'),
]


