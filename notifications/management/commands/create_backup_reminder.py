from django.core.management.base import BaseCommand

from notifications.models import Notification
from notifications.utils import create_notification


class Command(BaseCommand):
    help = "Create a global backup reminder notification."

    def handle(self, *args, **options):
        create_notification(
            title="Daily Backup Reminder",
            message="Please create and copy today’s clinic backup to an external drive before closing.",
            notification_type=Notification.NotificationType.BACKUP,
            is_global=True,
            link="/backups/",
        )

        self.stdout.write(self.style.SUCCESS("Backup reminder notification created."))