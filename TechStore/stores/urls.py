from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('tablet/', views.tablet_page, name='tablet'),
    path('laptop/', views.laptop_page, name='laptop'),
    path('manhinh/', views.manhinh_page, name='manhinh'),
    path('phukien/', views.phukien_page, name='phukien'),
    path('mayin/', views.mayin_page, name='mayin'),
    path('keyboard/', views.keyboard_page, name='keyboard'),
    path('mouse/', views.mouse_page, name='mouse'),

    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('personal/', views.personal_page, name='personal'),


]
