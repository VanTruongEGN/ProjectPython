# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, profile_view, logout_view, cart_view, add_to_cart, buy_now, cart_remove, \
    update_cart_quantity, process_checkout, change_password, profile_password_view, add_address, delete_address, \
    profile_address_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("profile/password/", profile_password_view, name="profile_password"),
    path("change-password/", change_password, name="change_password"),
    path("logout/", logout_view, name="logout"),    path("cart/", cart_view, name="cart"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", process_checkout, name="process_checkout"),
    path("add/<str:product_id>/", add_to_cart, name="add_to_cart"),
    path("buy-now/<str:product_id>/", buy_now, name="buy_now"),
    path("remove/<str:item_id>/", cart_remove, name="cart_remove"),
    path("update-quantity/<str:item_id>/<str:action>/", update_cart_quantity, name="update_cart_quantity"),
    path("add_addresses/", add_address, name="add_addresses"),
    path("delete-address/<str:address_id>/", delete_address, name="delete_address"),
    path("profile/address/", profile_address_view, name="profile_address"),

]
