from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
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

        permissions = (('view_contactmessage', 'Can view ContactMessage'),)

    def __str__(self):
        return "created=%s; email=%s; subject=%s; status=%s" % (self.created, self.email, self.subject, self.status)

    def set_status_closed(self):
        self.status = self.STATUS_CLOSED
        self.save()

    def set_status_active(self):
        self.status = self.STATUS_ACTIVE
        self.save()

    def set_status_spam(self):
        self.status = self.STATUS_SPAM
        self.save()
