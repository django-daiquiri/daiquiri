from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from daiquiri.core.utils import get_date_display, import_class


class ContactMessage(models.Model):


    STATUS_ACTIVE = 'ACTIVE'
    STATUS_CLOSED = 'CLOSED'
    STATUS_SPAM = 'SPAM'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'active'),
        (STATUS_CLOSED, 'closed'),
        (STATUS_SPAM, 'spam')
    )

    author = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    subject = models.CharField(max_length=256)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='contact_messages')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    created = models.DateTimeField(blank=True, null=True)

    message = models.TextField()

    class Meta:
        ordering = ('-created', 'author')

        verbose_name = _('Contact message')
        verbose_name_plural = _('Contact messages')

    def __str__(self):
        return f"created={self.created}; email={self.email}; subject={self.subject}; status={self.status}"

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def created_label(self):
        return get_date_display(self.created)

    def set_status_closed(self):
        self.status = self.STATUS_CLOSED
        self.save()

    def set_status_active(self):
        self.status = self.STATUS_ACTIVE
        self.save()

    def set_status_spam(self):
        self.status = self.STATUS_SPAM
        self.save()



def MessageFilter():
    return import_class(settings.ANNOUNCEMENT_MESSAGE_FILTER)

class AnnouncementMessage(models.Model):

    # alert types must correspond to the bootstrap alert types
    ALERT_TYPE_INFO = "info"
    ALERT_TYPE_WARNING = "warning"
    ALERT_TYPE_URGENT = "danger"

    ANNOUNCEMENT_TYPE_CHOICES = (
        (ALERT_TYPE_INFO, "info"),
        (ALERT_TYPE_WARNING, "warning"),
        (ALERT_TYPE_URGENT, "urgent"),
    )

    title = models.CharField(  # noqa: DJ001
        max_length=100, blank=True, null=True,
        verbose_name=_("Title")
    )
    announcement = models.TextField(
        verbose_name=_("Announcement")
    )
    announcement_type = models.CharField(
        max_length=8,
        choices=ANNOUNCEMENT_TYPE_CHOICES,
        default=ALERT_TYPE_INFO,
        verbose_name=_("Announcement type")
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated")
    )
    visible = models.BooleanField(
        default=False,
        verbose_name=_("Visible")
    )
    visibility_filter = models.CharField(
        max_length=50, default="no_filter",
        verbose_name="Visibility filter"
    )

    class Meta:
        ordering = ('-updated', 'title')

        verbose_name = _('Announcement message')
        verbose_name_plural = _('Announcement messages')

    def __str__(self):
        return f"{self.title}: '{self.announcement}'"

    def get_filter(self):
        return getattr(MessageFilter(), str(self.visibility_filter))
