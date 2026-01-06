from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = "Add group 'Managers'"

    def handle(self, *args, **kwargs) -> None:
        """
        Method to add Manager group in app
        """

        try:
            Group.objects.get(name="Менеджер")
            self.stdout.write(self.style.SUCCESS("Группа 'Менеджер' уже существует"))
        except ObjectDoesNotExist:
            # Permissions
            view_recipients = Permission.objects.get(codename="view_recipients")
            # Message permissions
            view_message = Permission.objects.get(codename="view_message")
            # Mailing permissions
            view_mailing = Permission.objects.get(codename="view_mailing")
            can_disabling_mailing = Permission.objects.get(codename="can_disabling_mailing")
            # User permissions
            can_deactivate_user = Permission.objects.get(codename="can_deactivate_user")

            manager_group = Group.objects.create(name="Менеджер")
            manager_group.save()
            manager_group.permissions.clear()
            manager_group.permissions.add(view_recipients, view_mailing, view_message, can_disabling_mailing,
                                          can_deactivate_user)
            manager_group.save()

            self.stdout.write(self.style.SUCCESS("Группа 'Менеджер' успешно создана"))