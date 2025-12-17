# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, profile_view, logout_view, change_password, update_profile, edit_profile

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("change-password/", change_password, name="change_password"),
    path("update-profile/", update_profile, name="update_profile"),
    path("edit-profile/", edit_profile, name="edit_profile"),

]
