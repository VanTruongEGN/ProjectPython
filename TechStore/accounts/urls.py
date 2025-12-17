# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, profile_view, logout_view, cart_view, add_to_cart ,buy_now, cart_remove, update_cart_quantity, process_checkout

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),    path("cart/", cart_view, name="cart"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", process_checkout, name="process_checkout"),
    path("add/<str:product_id>/", add_to_cart, name="add_to_cart"),
    path("buy-now/<str:product_id>/", buy_now, name="buy_now"),
    path("remove/<str:item_id>/", cart_remove, name="cart_remove"),
    path("update-quantity/<str:item_id>/<str:action>/", update_cart_quantity, name="update_cart_quantity"),

]
