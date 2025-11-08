
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Đường dẫn gốc của app sẽ gọi hàm views.home
]