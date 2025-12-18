
from django.urls import path
from . import views
from .views import product_page, add_address, delete_address

urlpatterns = [
    path('<str:category_name>/', product_page, name='productList'),

    path('product/<str:pk>/', views.product_detail, name='productDetail'),
    path('product/<str:pk>/addComment/', views.addComment, name="addComment"),

    path('search', views.product_list, name="search"),
    path("add_addresses/", add_address, name="add_addresses"),
    path("delete-address/<str:address_id>/", delete_address, name="delete_address"),
]

