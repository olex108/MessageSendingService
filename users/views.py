import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .forms import UserRegistrationForm, UserUpdateForm, CustomChangePasswordForm
from .models import User
from .services import send_welcome_email


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "user"
    template_name = "users/user_detail.html"


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomChangePasswordForm
    template_name = "users/password_change.html"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.request.user.id})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_update.html"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.object.pk})


class UserRegistrationView(CreateView):
    """CBV for registrate user with GET request"""

    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:login")

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Method update to create token and send email by function send_welcome_email()"""

        user = form.save()
        user.is_active = False
        user.user_permissions.clear()
        # create email verification of user
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email_confirm/{token}/"
        send_welcome_email(user.email, url)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        response = super().form_invalid(form)
        response.context_data["error_message"] = "Please correct the errors below."
        return response


def email_verification(request, token):
    """
    View function change param of field is_active and app user into user_group of user
    if token by request is equal token in database
    """

    user = get_object_or_404(User, token=token)
    user.is_active = True

    try:
        user_group = Group.objects.get(name="Пользователь")
        user.groups.add(user_group)
    except Exception as e:
        print(e)

    user.save()
    return redirect(reverse("users:login"))
