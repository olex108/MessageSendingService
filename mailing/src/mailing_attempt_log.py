from abc import ABC, abstractmethod
from mailing.models import Mailing, MailingAttempt
from datetime import datetime


class MailingAttemptSaver(ABC):
    """
    Abstract class that defines save result of mailing attempt
    """

    @abstractmethod
    def save(self) -> None: ...


class DBMailingAttemptSaver(MailingAttemptSaver):
    """
    Class that defines save result of mailing attempt to database
    """

    mailing: Mailing

    def __init__(self, mailing: Mailing, status: str, response: str = "Успешная рассылка") -> None:

        self.mailing = mailing

        if status in ["SUCCESS", "FAILURE"]:
            self.status = status
        else:
            raise ValueError("Invalid status")

        self.response = response

    def save(self) -> None:

        MailingAttempt.objects.create(
            attempt_at=datetime.now(),
            mailing=self.mailing,
            status=self.status,
            response=self.response,
        )
