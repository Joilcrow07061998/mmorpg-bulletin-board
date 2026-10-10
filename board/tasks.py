import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job

from .models import Post


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")



@register_job(scheduler, "interval", weeks=1, id="weekly_newsletter", replace_existing=True, max_instances=3, coalesce=True)
def send_weekly_newsletter():
    #print("=== ПЛАНИРОВЩИК ЗАПУСТИЛСЯ, ПРОВЕРЯЮ ПОСТЫ ===")
    one_week_ago = timezone.now() - datetime.timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=one_week_ago)

    if not posts.exists():
        #print("Постов за неделю не найдено, выхожу из функции.")
        return

    subscribers_emails = list(User.objects.filter(is_active=True).values_list('email', flat=True))

    subscribers_emails = [email for email in subscribers_emails if email]

    if not subscribers_emails:
        return

    posts_summary = ""
    for post in posts:
        posts_summary += f"• [{post.category.name}] {post.headline}\n"
        posts_summary += f"  Читать полностью: http://127.0.0{post.pk}/\n\n"

    message_text = f"""Привет, Игрок!

Вот список новых объявлений на MMORPG Board за прошедшую неделю:

{posts_summary}
Удачной охоты на просторах игровых миров!
Команда Guild Board."""

    send_mail(
        subject='Еженедельный дайджест новых объявлений MMORPG Board',
        message=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=subscribers_emails,
        fail_silently=False,
    )


scheduler.start()
