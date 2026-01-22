# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, profile_view, logout_view, cart_view, add_to_cart, buy_now, cart_remove, update_cart_quantity, process_checkout, change_password, profile_password_view, add_address, forgot_password_view, verify_otp_view, reset_new_password_view, delete_address, profile_address_view, profile_orders
from products.views import product_detail
from . import views

urlpatterns = [
    # Password Reset (OTP Flow)
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path("reset-new-password/", reset_new_password_view, name="reset_new_password"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("profile/password/", profile_password_view, name="profile_password"),
    path("profile/orders/", profile_orders, name="profile_orders"),
    path('product/<str:pk>/',product_detail, name='productDetail'),
    path("change-password/", change_password, name="change_password"),
    path("logout/", logout_view, name="logout"),    path("cart/", cart_view, name="cart"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", process_checkout, name="process_checkout"),
    path("add/<str:product_id>/", add_to_cart, name="add_to_cart"),
    path("buy-now/<str:product_id>/", buy_now, name="buy_now"),
    path("remove/<str:item_id>/", cart_remove, name="cart_remove"),
    path("update-quantity/<str:item_id>/<str:action>/", update_cart_quantity, name="update_cart_quantity"),
    path("add_addresses/", add_address, name="add_addresses"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/address/", views.profile_address_view, name="profile_address"),
    path("profile/address/delete/<str:address_id>/", views.delete_address, name="delete_address"),
    path("profile/address/default/<str:address_id>/", views.set_default_address, name="set_default_address"),
    path("orders/cancel/<str:order_id>/", views.cancel_order, name="cancel_order"),
    path("profile/orders/cancelled/",views.profile_cancelled_orders,name="profile_cancelled_orders"),
    path("create-vnpay-payment/", views.create_vnpay_payment, name="create_vnpay_payment"),
    path("vnpay_return/", views.vnpay_return, name="vnpay_return"),

]


