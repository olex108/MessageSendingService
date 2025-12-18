from django.db import models

from users.models import User


class Recipients(models.Model):
    """Model to create, view, update, delete recipient of mailing"""

    email = models.EmailField(verbose_name="Почта")
    full_name = models.CharField(max_length=150, verbose_name="Полное имя получателя")
    comment = models.TextField(verbose_name="Комментарии", blank=True, null=True)
    mailer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель")

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["email"]


class Message(models.Model):
    """Model to create, view, update, delete message of mailing"""

    title = models.CharField(max_length=150, verbose_name="Тема письма")
    content = models.TextField(verbose_name="Тело письма", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    def __str__(self):
        return f"{self.title}-{self.author}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["title"]


class Mailing(models.Model):
    """Model to create, view, update, delete mailing items"""

    CREATED = "CREATED"
    LAUNCHED = "LAUNCHED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = (
        (CREATED, "Создана"),
        (LAUNCHED, "Запущена"),
        (COMPLETED, "Завершена"),
    )

    start_at = models.DateTimeField(verbose_name="Дата и время начала")
    end_at = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(verbose_name="Статус рассылки", max_length=10, choices=STATUS_CHOICES, default=CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipients, verbose_name="Получатели", blank=True, null=True)

    def __str__(self):
        return f"{self.message} - {self.status} - {self.start_at} - {self.end_at}"

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ["start_at"]


class MailingAttempt(models.Model):
    """Model to seva date, time, status and response of mailing server for mailing attempt"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    STATUS_CHOICES = (
        (SUCCESS, "Успешно"),
        (FAILED, "Не успешно"),
    )

    attempt_at = models.DateTimeField(verbose_name="Дата и время попытки", auto_now_add=True)
    status = models.CharField(verbose_name="Статус рассылки", max_length=10, choices=STATUS_CHOICES)
    response = models.TextField(verbose_name="Ответ почтового сервера", blank=True, null=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")

    def __str__(self):
        return f"{self.mailing} - {self.status} - {self.attempt_at}"

    class Meta:
        verbose_name = "попытка"
        verbose_name_plural = "попытки"
        ordering = ["attempt_at"]
