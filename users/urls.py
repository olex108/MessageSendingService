from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path

from . import views
from .forms import CustomAuthenticationForm, CustomChangePasswordForm

app_name = "users"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html", authentication_form=CustomAuthenticationForm),
        name="login",
    ),
    path("registration/", views.UserRegistrationView.as_view(), name="registration"),
    path("logout/", LogoutView.as_view(next_page="users:login"), name="logout"),
    path("users/email_confirm/<str:token>/", views.email_verification, name="email_confirm"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/password_change/", views.UserPasswordChangeView.as_view(), name="user_password_change"),
]
