from django import template

from daiquiri.contact.models import AnnouncementMessage

register = template.Library()


@register.inclusion_tag("contact/announcements.html", takes_context=True)
def show_announcements(context):
    request = context["request"]
    announcements = AnnouncementMessage.objects.filter(visible=True)
    announcements = [msg for msg in announcements if msg.get_filter()(request) is True]
    return {
        "announcements": announcements,
    }
