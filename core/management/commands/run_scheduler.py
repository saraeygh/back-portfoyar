from django.core.management.base import BaseCommand

from core.scheduled_jobs import blocking_scheduler


class Command(BaseCommand):
    help = "Run scheduled tasks"

    def handle(self, *args, **options):
        blocking_scheduler()
