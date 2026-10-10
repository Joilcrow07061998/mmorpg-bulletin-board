from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import register_events

from board.scheduling import configure_scheduler


class Command(BaseCommand):
    help = "Run the weekly newsletter scheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        configure_scheduler(scheduler)
        register_events(scheduler)

        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
