
from django.urls import path
from . import views
from .views import product_page

urlpatterns = [
    path('<str:category_name>/', product_page, name='product_list')
]
