from abc import ABC, abstractmethod

from django.core.mail import send_mail

from mailing.models import Mailing, MailingAttempt

import os
from datetime import datetime


class MailingHandler(ABC):
    """
    Abstract class for handling mailing
    """

    @abstractmethod
    def send_mails(self) -> bool: ...

    @abstractmethod
    def _create_mailing_attempt_object(self, status: str, server_response: str) -> None: ...


class SMTPMailingHandler(MailingHandler):
    """
    SMTP Mailing Handler that sends emails via SMTP server.
    """

    mailing: Mailing

    def __init__(self, mailing: Mailing) -> None:
        self.mailing = mailing

    def send_mails(self) -> bool:
        """
        Sends emails via SMTP server.
        """

        subject = self.mailing.message.title
        message = self.mailing.message.content
        from_email = os.getenv("EMAIL_ADDRESS")
        recipient_list = [recipient.email for recipient in self.mailing.recipients.all()]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            self._create_mailing_attempt_object(status=MailingAttempt.SUCCESS)
            self._change_mailing_status(Mailing.COMPLETED)
            return True

        except Exception as e:
            self._create_mailing_attempt_object(status=MailingAttempt.FAILED, server_response=str(e))
            return False

    def _create_mailing_attempt_object(self, status: str, server_response: str = "Успешно") -> None:
        """
        Creates Mailing Attempt object with results of sending mails via SMTP server.
        """

        MailingAttempt.objects.create(
            attempt_at=datetime.now(),
            mailing=self.mailing,
            status=status,
            response=server_response,
        )

    def _change_mailing_status(self, status: str) -> None:
        """
        Changes Mailing status by COMPLETED
        """

        self.mailing.status = status
        self.mailing.save()
