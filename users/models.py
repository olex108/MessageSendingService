from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Model of user representing with field email for authentication of user"""

    users = None
    email = models.EmailField(unique=True, verbose_name="Почта")
    country = models.CharField(max_length=30, verbose_name="Название страны")
    phone = PhoneNumberField(verbose_name="Телефон", null=True, blank=True)
    avatar = models.ImageField(
        upload_to="users/avatar/", verbose_name="Аватар", help_text="Загрузите аватар", blank=True, null=True
    )

    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
