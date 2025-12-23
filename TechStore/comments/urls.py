
from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:pk>/review_chart/', views.review_chart, name='review_chart'),
]

