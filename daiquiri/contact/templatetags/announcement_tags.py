from django import template
from daiquiri.contact.models import AnnouncementMessage

register = template.Library()


@register.inclusion_tag("contact/announcements.html")
def show_announcements():
    announcements = AnnouncementMessage.objects.filter(visible=True)
    return {
        "announcements": announcements,
    }
