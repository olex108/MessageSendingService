import secrets

from django.http import HttpResponseForbidden

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, UpdateView

from .forms import UserRegistrationForm, UserUpdateForm, CustomChangePasswordForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import User
from .services import send_welcome_email

from mailing.src.cache_decorators import get_cache_cotext_for_user, get_cache_queryset_for_user


class UsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """CBV for users list"""

    model = User
    context_object_name = "users"
    template_name = "users/users_list.html"

    @get_cache_queryset_for_user("users_list")
    def get_queryset(self):
        return User.objects.all().filter(groups__name="Пользователь")

    def test_func(self):
        return self.request.user.has_perm("users.can_deactivate_user")

    def handle_no_permission(self):
        return redirect("mailing:home")


class UserDeactivateView(LoginRequiredMixin, View):
    """CBV for deactivate user"""

    def post(self, request, pk : int = None):
        user = get_object_or_404(User, id=pk)

        if not request.user.has_perm('users.can_deactivate_user'):
            return HttpResponseForbidden("У вас нет прав для блокировки пользователя")

        user.is_active = False if user.is_active else True
        user.save()

        return redirect('users:users_list')


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "user"
    template_name = "users/user_detail.html"


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomChangePasswordForm
    template_name = "users/password_change.html"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.request.user.id})


class UserPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html",
    email_template_name = "users/password_reset_email.html",
    form_class = CustomPasswordResetForm,
    success_url = reverse_lazy("users:password_reset_done")


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm,
    template_name = "users/password_reset_confirm.html",
    success_url = reverse_lazy("users:password_reset_complete")


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
