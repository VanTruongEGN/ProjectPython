from django.contrib import admin
from django.urls import path, include

from products.views import product_page
from . import views
from .views import search_product

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('personal/', views.personal_page, name='personal'),
    path('api/cart/available-stores/', views.get_available_stores_for_cart, name='api_cart_available_stores'),

    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),




]
