import os

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand

from mailing.models import Recipients, Message, Mailing, MailingAttempt
from users.models import User


class Command(BaseCommand):
    help = "Add data for test"

    def handle(self, *args, **kwargs) -> None:
        """
        Method to delete and add superusers, users, groups, data to mailing app
        """

        # Delete data
        Recipients.objects.all().delete()
        Mailing.objects.all().delete()
        Message.objects.all().delete()
        MailingAttempt.objects.all().delete()


        User.objects.all().delete()
        Group.objects.all().delete()

        print("Delete all data")

        # Create superuser with email address with send mails
        superuser1 = User.objects.create(email=os.getenv("EMAIL_ADDRESS"), id=5)
        superuser1.set_password("1234qwer")
        superuser1.is_active = True
        superuser1.is_staff = True
        superuser1.is_superuser = True
        superuser1.save()
        #
        superuser2 = User.objects.create(email="superuser@test.com", id=6)
        superuser2.set_password("1234qwer")
        superuser2.is_active = True
        superuser2.is_staff = True
        superuser2.is_superuser = True
        superuser2.save()

        # Permissions
        # Recipients permissions
        add_recipients = Permission.objects.get(codename="add_recipients")
        change_recipients = Permission.objects.get(codename="change_recipients")
        delete_recipients = Permission.objects.get(codename="delete_recipients")
        view_recipients = Permission.objects.get(codename="view_recipients")

        # Message permissions
        add_message = Permission.objects.get(codename="add_message")
        change_message = Permission.objects.get(codename="change_message")
        delete_message = Permission.objects.get(codename="delete_message")
        view_message = Permission.objects.get(codename="view_message")

        # Mailing permissions
        add_mailing = Permission.objects.get(codename="add_mailing")
        change_mailing = Permission.objects.get(codename="change_mailing")
        delete_mailing = Permission.objects.get(codename="delete_mailing")
        view_mailing = Permission.objects.get(codename="view_mailing")
        can_send_mailing = Permission.objects.get(codename="can_send_mailing")
        can_disabling_mailing = Permission.objects.get(codename="can_disabling_mailing")

        # Create groups
        user_group = Group.objects.create(name="Пользователь")
        user_group.save()
        user_group.permissions.clear()
        user_group.permissions.add(add_recipients, change_recipients, delete_recipients, add_message,
                                   change_message, delete_message, add_mailing, change_mailing,
                                   delete_mailing, can_send_mailing, can_disabling_mailing)

        manager_group = Group.objects.create(name="Менеджер")
        manager_group.save()
        manager_group.permissions.clear()
        manager_group.permissions.add(view_recipients, view_mailing, view_message, can_disabling_mailing)
        manager_group.save()

        # Create users
        user_1 = User.objects.create(email="user_1@test.com", id=1)
        user_1.set_password("1234qwer")
        user_1.is_active = True
        user_1.is_staff = False
        user_1.is_superuser = False
        user_1.save()

        user_2 = User.objects.create(email="user_2@test.com", id=2)
        user_2.set_password("1234qwer")
        user_2.is_active = True
        user_2.is_staff = False
        user_2.is_superuser = False
        user_2.save()

        user_3 = User.objects.create(email="user_3@test.com", id=3)
        user_3.set_password("1234qwer")
        user_3.is_active = True
        user_3.is_staff = False
        user_3.is_superuser = False
        user_3.save()

        user_4 = User.objects.create(email="user_4@test.com", id=4)
        user_4.set_password("1234qwer")
        user_4.is_active = True
        user_4.is_staff = True
        user_4.is_superuser = False
        user_4.save()

        # Add users into groups
        user_1.groups.add(user_group)
        user_2.groups.add(user_group)
        user_3.groups.add(user_group)
        user_4.groups.add(manager_group)

        # Load data from fixtures
        call_command("loaddata", "db_fixtures/recipients_fixtures.json")
        call_command("loaddata", "db_fixtures/message_fixtures.json")
        call_command("loaddata", "db_fixtures/mailing_fixtures.json")
        call_command("loaddata", "db_fixtures/mailing_attempt_fixtures.json")

        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))
