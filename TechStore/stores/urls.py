from django.contrib import admin
from django.urls import path
from . import views
from accounts import views as account_views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('tablet/', views.tablet_page, name='tablet'),
    path('keyboard/', views.keyboard, name='keyboard'),
    path('laptop/', views.laptop, name='laptop'),
    path('manhinh/', views.manhinh, name='manhinh'),
    path('mayin/', views.mayin, name='mayin'),
    path('mouse/', views.mouse, name='mouse'),
    path('phukien/', views.phukien, name='phukien'),

    path('register/', account_views.register, name='register'),
    path('personal-page/', account_views.personal, name='personal'),
    path('login/', account_views.login, name='login'),
]
