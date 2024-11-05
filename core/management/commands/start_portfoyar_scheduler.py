from django.core.management.base import BaseCommand

from core.portfoyar_scheduler_util import portfoyar_scheduler


class Command(BaseCommand):
    help = "Start portfoyar_scheduler"

    def handle(self, *args, **options):

        portfoyar_scheduler()
