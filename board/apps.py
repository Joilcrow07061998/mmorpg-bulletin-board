import os
import sys

from django.apps import AppConfig


class BoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'board'

    def ready(self):
        if len(sys.argv) < 2 or sys.argv[1] != 'runserver':
            return

        if os.environ.get('RUN_MAIN') != 'true' and '--noreload' not in sys.argv:
            return

        from apscheduler.schedulers.background import BackgroundScheduler
        from django.conf import settings

        from .scheduling import configure_scheduler

        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        configure_scheduler(scheduler)
        scheduler.start()
