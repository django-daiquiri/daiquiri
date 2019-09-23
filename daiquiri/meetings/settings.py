from django.utils.translation import ugettext_lazy as _

MEETINGS_CONTRIBUTION_TYPES = [
    ('talk', _('Talk')),
    ('poster', _('Poster'))
]
MEETINGS_PAYMENT_CHOICES = (
    ('cash', _('cash')),
    ('wire', _('wire transfer')),
)

MEETINGS_PARTICIPANT_DETAIL_KEYS = []
MEETINGS_ABSTRACT_MAX_LENGTH = 2000
