from mailing.src.mailing_handlers import SMTPMailingHandler

from .models import Mailing, MailingAttempt, Recipients
from users.models import User
from mailing.src.mailing_attempt_log import DBMailingAttemptSaver

from django.db.models import Count


class MailingServices:

    @staticmethod
    def start_mailing(mailing: Mailing) -> str:
        mailing_sending = SMTPMailingHandler(mailing)
        result = mailing_sending.send_mails()
        if result == MailingAttempt.SUCCESS:
            mailing_attempt_saver = DBMailingAttemptSaver(
                mailing,
                status=MailingAttempt.SUCCESS,
            )
            mailing_attempt_saver.save()
            return "Рассылка запущена успешно"

        else:
            mailing_attempt_saver = DBMailingAttemptSaver(
                mailing,
                status=MailingAttempt.FAILED,
                response=result,
            )
            mailing_attempt_saver.save()
            return "Ошибка рассылки"


    @staticmethod
    def get_homa_page_data(context: dict, user: User) -> dict:

        context["Recipients_count"] = Recipients.objects.all().filter(mailer=user).count()
        context["Mailings_count"] = Mailing.objects.all().filter(message__author=user).count()
        context["Mailings_active_count"] = Mailing.objects.all().filter(
            message__author=user,
            status="LAUNCHED"
        ).count()

        return context


    @staticmethod
    def get_statistics(context: dict, user: User) -> dict:

        user_mailing_attempts_qs = MailingAttempt.objects.all().filter(mailing__message__author=user)
        user_success_mailing_attempts = user_mailing_attempts_qs.filter(status="SUCCESS")
        context["Success_count"] = user_success_mailing_attempts.count()
        context["Failed_count"] = user_mailing_attempts_qs.filter(status="FAILED").count()
        context["Recipients_count"] = user_success_mailing_attempts.aggregate(total=Count('mailing__recipients'))['total']

        return context
