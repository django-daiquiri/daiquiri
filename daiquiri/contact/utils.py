from daiquiri.core.utils import send_mail
from daiquiri.auth.utils import get_admin_emails


def send_contact_message(request, message):

    emails = get_admin_emails()
    context = {
        'user': message.user,
        'author': message.author,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
    }
    send_mail(request, 'contact/email/new_message_admin', context, emails)
    send_mail(request, 'contact/email/new_message_user', context, [message.email])
