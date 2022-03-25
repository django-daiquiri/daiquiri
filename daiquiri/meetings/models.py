from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Meeting(models.Model):

    title = models.CharField(
        max_length=256,
        verbose_name=_('Title'),
        help_text=_('Title of the meeting')
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('Slug'),
        help_text=_('Slug for the URL of the meeting')
    )
    registration_message = models.TextField(
        blank=True, null=True,
        verbose_name=_('Registration message'),
        help_text=_('Message on registration page, you can use Markdown here.')
    )
    registration_done_message = models.TextField(
        blank=True, null=True,
        verbose_name=_('Registration done message'),
        help_text=_('Message on the page displayed after registration, you can use Markdown here.')
    )
    participants_message = models.TextField(
        blank=True, null=True,
        verbose_name=_('Participants message'),
        help_text=_('Message on participants page, you can use Markdown here.')
    )
    contributions_message = models.TextField(
        blank=True, null=True,
        verbose_name=_('Contributions message'),
        help_text=_('Message on contributions page, you can use Markdown here.')
    )
    registration_open = models.BooleanField(
        default=False,
        verbose_name=_('Registration open'),
        help_text=_('Designates whether the registration page is publicly accessible.')
    )
    participants_open = models.BooleanField(
        default=False,
        verbose_name=_('Participants list open'),
        help_text=_('Designates whether the participants page is publicly accessible.')
    )
    contributions_open = models.BooleanField(
        default=False,
        verbose_name=_('Contributions list open'),
        help_text=_('Designates whether the contributions page is publicly accessible.')
    )

    class Meta:
        ordering = ('title', )

        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')

    def __str__(self):
        return self.title


class Participant(models.Model):

    STATUS_ORGANIZER = 'ORGANIZER'
    STATUS_DISCUSSION_LEADER = 'DISCUSSION_LEADER'
    STATUS_INVITED = 'INVITED'
    STATUS_REGISTERED = 'REGISTERED'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CANCELED = 'CANCELED'

    STATUS_CHOICES = (
        (STATUS_ORGANIZER, _('organizer')),
        (STATUS_DISCUSSION_LEADER, _('discussion leader')),
        (STATUS_INVITED, _('invited')),
        (STATUS_REGISTERED, _('registered')),
        (STATUS_ACCEPTED, _('accepted')),
        (STATUS_REJECTED, _('rejected')),
        (STATUS_CANCELED, _('canceled')),
    )

    meeting = models.ForeignKey(
        Meeting, related_name='participants', on_delete=models.CASCADE,
        verbose_name=_('Meeting'),
        help_text=_('Meeting this participant has registered for'),
    )
    first_name = models.CharField(
        max_length=256,
        verbose_name=_('First name'),
    )
    last_name = models.CharField(
        max_length=256,
        verbose_name=_('Last name'),
    )
    email = models.EmailField(
        max_length=256,
        verbose_name=_('Email'),
    )
    details = models.JSONField(
        null=True, blank=True, default=dict,
        verbose_name=_('Details'),
        help_text=_('Choices are given by settings.MEETINGS_PARTICIPANT_DETAIL_KEYS')
    )
    registered = models.DateTimeField(
        verbose_name=_('Registered on'),
        help_text=_('Datetime this participant has submitted his/her registration')
    )
    status = models.CharField(
        max_length=32, choices=STATUS_CHOICES,
        verbose_name=_('Status'),
        help_text=_('Status of the participant.')
    )
    payment = models.CharField(
        max_length=32, blank=True,
        verbose_name=_('Payment'),
        help_text=_('Type of payment for the participant.')
    )
    payment_complete = models.BooleanField(
        default=False,
        verbose_name=_('Payment complete'),
        help_text=_('Designates whether the payment is completed.')
    )

    class Meta:
        ordering = ('meeting', 'last_name', 'first_name')

        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')

    def __str__(self):
        return '%s (%s)' % (self.full_name, self.meeting)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def as_text(self):
        values = [
            (_('Name'), self.full_name),
            (_('Email'), self.email)
        ]
        for detail_key in settings.MEETINGS_PARTICIPANT_DETAIL_KEYS:
            if self.details[detail_key['key']]:
                values.append((detail_key['label'], self.details[detail_key['key']]))

        return '\n' + ''.join(['%s: %s\n' % value for value in values])


    def get_payment_display(self):
        try:
            return dict(settings.MEETINGS_PAYMENT_CHOICES)[self.payment]
        except KeyError:
            return ''


class Contribution(models.Model):

    participant = models.ForeignKey(
        Participant, related_name='contributions', on_delete=models.CASCADE,
        verbose_name=_('Participant'),
        help_text=_('Participant who submitted this contribution')
    )
    title = models.CharField(
        max_length=256,
        verbose_name=_('Title')
    )
    abstract = models.TextField(
        verbose_name=_('Abstract')
    )
    contribution_type = models.CharField(
        max_length=8, blank=True,
        verbose_name=_('Contribution type'),
        help_text=_('Choices are given by settings.MEETINGS_CONTRIBUTION_TYPES')
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name=_('Accepted'),
        help_text=_('Designates whether the contribution is accepted.')
    )

    class Meta:
        ordering = ('participant', 'title')

        verbose_name = _('Contribution')
        verbose_name_plural = _('Contributions')

    def __str__(self):
        return self.title

    @property
    def as_text(self):
        values = [
            (_('Type'), dict(settings.MEETINGS_CONTRIBUTION_TYPES)[self.contribution_type]),
            (_('Title'), self.title),
            (_('Abstract'), self.abstract)
        ]
        return '\n' + ''.join(['%s: %s\n' % value for value in values])

    def get_contribution_type_display(self):
        try:
            return dict(settings.MEETINGS_CONTRIBUTION_TYPES)[self.contribution_type]
        except KeyError:
            return ''
