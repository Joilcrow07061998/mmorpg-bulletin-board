from django_apscheduler.jobstores import DjangoJobStore

from .tasks import send_weekly_newsletter


def configure_scheduler(scheduler):
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
    return scheduler
