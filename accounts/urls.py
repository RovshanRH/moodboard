from django.urls import path

from .views import auth_view, login_page, logout_page, register_page


app_name = "accounts"

urlpatterns = [
    path("register/", register_page, name="register"),
    path("login/", login_page, name="login"),
    path("logout/", logout_page, name="logout"),
    path("api/auth/", auth_view, name="auth"),
]
