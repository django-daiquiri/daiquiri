from daiquiri.core.utils import send_mail, get_admin_emails, get_permission_emails


def get_manager_emails():
    return get_permission_emails((
        'daiquiri_meetings.view_meeting',
        'daiquiri_meetings.view_participant',
        'daiquiri_meetings.view_contribution',
    )) + get_admin_emails()


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
