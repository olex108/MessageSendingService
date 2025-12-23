import os
from abc import ABC, abstractmethod
from datetime import datetime

from django.core.mail import send_mail

from mailing.models import Mailing, MailingAttempt


class MailingHandler(ABC):
    """
    Abstract class for handling mailing
    """

    @abstractmethod
    def send_mails(self) -> str: ...

    @abstractmethod
    def __change_mailing_status(self, status: str) -> None: ...


class SMTPMailingHandler(MailingHandler):
    """
    SMTP Mailing Handler that sends emails via SMTP server.
    """

    mailing: Mailing

    def __init__(self, mailing: Mailing) -> None:
        self.mailing = mailing

    def send_mails(self) -> str:
        """
        Sends emails via SMTP server. Return "Success" if sent successfully or response of server if failed."
        """

        subject = self.mailing.message.title
        message = self.mailing.message.content
        from_email = os.getenv("EMAIL_ADDRESS")
        recipient_list = [recipient.email for recipient in self.mailing.recipients.all()]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            self.__change_mailing_status(Mailing.COMPLETED)
            return "SUCCESS"
        except Exception as e:
            return str(e)

    def __change_mailing_status(self, status: str) -> None:
        """
        Changes Mailing status by COMPLETED
        """

        self.mailing.status = status
        self.mailing.save()
