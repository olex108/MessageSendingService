from django.core.management.base import BaseCommand

from mailing.models import Mailing

from mailing.src.mailing_handlers import SMTPMailingHandler


class Command(BaseCommand):
    help = "Starts the mailing process"

    def handle(self, *args, **options) -> None:
        """
        Method to start the mailing process, print list of valid mailings, ask user print number of mailings to start
        """

        mailing_counter = 1
        mailing_launched_list = []

        for mailing in Mailing.objects.all():
            mailing.update_status()
            if mailing.status == Mailing.LAUNCHED:
                mailing_launched_list.append(mailing)
                print(f"{mailing_counter} - {mailing.message.title} - {mailing.status} - {mailing.start_at}")
                mailing_counter += 1

        if mailing_counter == 1:
            print("У Вас нет рассылок готовых к запуску")
        else:
            while True:
                mailing_num = input("Введите номер рассылки для запуска: ")
                try:
                    if int(mailing_num) - 1 in range(mailing_counter):
                        mailing_sending = SMTPMailingHandler(mailing_launched_list[int(mailing_num) - 1])
                        mailing_sending.send_mails()
                        break
                    else:
                        print("Неверный номер рассылки")
                except ValueError:
                    print("Неверный номер рассылки")
