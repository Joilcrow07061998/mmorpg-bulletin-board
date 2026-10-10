from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore

from board.tasks import send_weekly_newsletter


class Command(BaseCommand):
    help = "Run the weekly newsletter scheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.add_job(
            send_weekly_newsletter,
            trigger="interval",
            weeks=1,
            id="weekly_newsletter",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
