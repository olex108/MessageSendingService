from mailing.models import Mailing, MailingAttempt, Recipients
from users.models import User

from django.db.models import Count, Q


class MailingAppQueries:
    """Class with queries to database for pages"""

    @staticmethod
    def get_homa_page_data(context: dict, user: User = None) -> dict:
        if user.has_perm("mailing.view_mailing"):
            context["Recipients_count"] = Recipients.objects.all().count()
            context["Mailings_count"] = Mailing.objects.all().count()
            context["Mailings_active_count"] = Mailing.objects.all().filter(
                status="LAUNCHED"
            ).count()
        else:
            context["Recipients_count"] = Recipients.objects.all().filter(mailer=user).count()
            context["Mailings_count"] = Mailing.objects.all().filter(message__author=user).count()
            context["Mailings_active_count"] = Mailing.objects.all().filter(
                message__author=user,
                status="LAUNCHED"
            ).count()

        return context

    @staticmethod
    def get_statistics(context: dict, user: User) -> dict:
        if user.has_perm("mailing.view_mailing"):
            stats = MailingAttempt.objects.aggregate(
                success_count=Count('id', filter=Q(status="SUCCESS")),
                failed_count=Count('id', filter=Q(status="FAILED")),
                recipients_count=Count('mailing__recipients', filter=Q(status="SUCCESS"))
            )

            context["Success_count"] = stats['success_count']
            context["Failed_count"] = stats['failed_count']
            context["Recipients_count"] = stats['recipients_count']

        else:
            # 1. Сначала делаем базовый QuerySet с фильтром по юзеру
            base_qs = MailingAttempt.objects.filter(mailing__message__author=user)

            # 2. Делаем ОДИН запрос к базе, который посчитает всё сразу
            stats = base_qs.aggregate(
                success_count=Count('id', filter=Q(status="SUCCESS")),
                failed_count=Count('id', filter=Q(status="FAILED")),
                # Считаем количество получателей только для успешных рассылок
                recipients_count=Count('mailing__recipients', filter=Q(status="SUCCESS"))
            )

            # 3. Наполняем контекст (если aggregate вернет None, заменяем на 0)
            context["Success_count"] = stats['success_count'] or 0
            context["Failed_count"] = stats['failed_count'] or 0
            context["Recipients_count"] = stats['recipients_count'] or 0

        return context
