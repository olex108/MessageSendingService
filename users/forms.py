from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import ModelForm

from .models import User


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "country", "avatar"]

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "example@example.com",
            }
        )
        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Имя",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Фамилия",
            }
        )
        self.fields["country"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Название страны",
            }
        )
        self.fields["country"].help_text = ""
        self.fields["phone"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "+77777777777",
            }
        )
        self.fields["avatar"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2", "country", "phone", "avatar"]

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "example@example.com",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "label": "Пароль:",
                "placeholder": "Введите пароль",
            }
        )
        self.fields["password1"].label = "Пароль"
        self.fields["password1"].help_text = "Введите сложный пароль"
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )
        self.fields["password2"].label = "Пароль повторно"
        self.fields["password2"].help_text = ""
        self.fields["country"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Название страны",
            }
        )
        self.fields["country"].help_text = ""
        self.fields["phone"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "+77777777777",
            }
        )
        self.fields["avatar"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


class CustomAuthenticationForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
