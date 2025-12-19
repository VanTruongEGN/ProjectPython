# sentiment/urls.py
from django.urls import path
from .views import sentiment_api

urlpatterns = [
    path("predict/", sentiment_api),
]
