from django.contrib.auth.models import User

from daiquiri.core.utils import send_mail


def get_manager_emails():
    return [user.email for user in User.objects.filter(groups__name='meetings_manager')]


def send_registration_mails(request, meeting, participant, contribution=None):
    # sends an email to the admins once a user was activated.
    send_mail(request, 'meetings/email/notify_registration', {
        'meeting': meeting,
        'participant': participant,
        'contribution': contribution
    }, get_manager_emails())

    # sends an email to the once he/she was activated.
    send_mail(request, 'meetings/email/registration', {
        'meeting': meeting,
        'participant': participant,
        'contribution': contribution
    }, [participant.email])
