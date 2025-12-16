
from django.urls import path
from . import views
from .views import product_page

urlpatterns = [
    path('<str:category_name>/', product_page, name='productList'),

    path('product/<str:pk>/', views.product_detail, name='productDetail'),
    # path('product/<int:product_id>/', views.addComment, name="addComment"),

]

