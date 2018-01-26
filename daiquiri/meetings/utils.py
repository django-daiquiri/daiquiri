from django.contrib.auth.models import User

from daiquiri.core.utils import send_mail


def get_manager_emails():
    return [user.email for user in User.objects.filter(groups__name='meetings_manager')]


def send_registration_mails(request, meeting, participant):

    # sends an email to the admins once a user was activated.
    send_mail(request, 'meetings/email/notify_registration', {
        'title': meeting.title,
        'full_name': participant.full_name,
        'values': participant.values
    }, get_manager_emails())

    # sends an email to the once he/she was activated.
    send_mail(request, 'meetings/email/registration', {
        'title': meeting.title,
        'full_name': participant.full_name,
        'values': participant.values
    }, [participant.email])
