from django import template
from django.utils.safestring import mark_safe

from board.sanitizers import sanitize_post_body


register = template.Library()


@register.filter
def sanitize_html(value):
    return mark_safe(sanitize_post_body(value))
