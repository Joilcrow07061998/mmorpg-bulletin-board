import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import Post


def send_weekly_newsletter():
    one_week_ago = timezone.now() - datetime.timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=one_week_ago)

    if not posts.exists():
        return

    subscribers_emails = list(
        User.objects.filter(is_active=True).values_list('email', flat=True)
    )
    subscribers_emails = [email for email in subscribers_emails if email]

    if not subscribers_emails:
        return

    posts_summary = ""
    for post in posts:
        post_url = f"{settings.SITE_URL}{reverse('board:post_detail', kwargs={'pk': post.pk})}"
        posts_summary += f"• [{post.category.name}] {post.headline}\n"
        posts_summary += f"  Читать полностью: {post_url}\n\n"

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
