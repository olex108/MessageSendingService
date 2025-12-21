from django import forms

from datetime import datetime
from django.utils import timezone


def validate_mailing_start(start_at: datetime) -> None:
    """Validate mailing start date and time"""

    if start_at < timezone.now():
        raise forms.ValidationError("Начало рассылки не может быть в прошедшем времени")


def validate_mailing_end(start_at: datetime, end_at: datetime) -> None:
    """Validate mailing start and end dates and time"""

    if start_at > end_at:
        raise forms.ValidationError("Завершение рассылки не может быть раньше начала")
