from django.contrib import admin
from django.urls import path

from products.views import product_page
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('personal/', views.personal_page, name='personal'),


]
