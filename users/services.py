import os

from django.core.mail import send_mail


def send_welcome_email(user_email: str, url: str) -> None:
    subject = 'Добро пожаловать в сервис "Рассылка"'
    message = f"""Спасибо что зарегистрировались в нашем сервисе! Перейдите по ссылке для подтверждения почты {url}.
Теперь вы можете создавать и редактировать позиции по сайту"""
    from_email = os.getenv("EMAIL_ADDRESS")
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)
