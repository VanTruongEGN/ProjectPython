# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, cart_view, checkout_view, add_to_cart ,buy_now, cart_remove
urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("add/<str:product_id>/", add_to_cart, name="add_to_cart"),
    path("buy-now/<str:product_id>/", buy_now, name="buy_now"),
    path("remove/<str:item_id>/", cart_remove, name="cart_remove"),

]
