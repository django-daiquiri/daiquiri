from django.urls import reverse

from daiquiri.core.utils import get_admin_emails, get_permission_emails, send_mail


def get_manager_emails():
    return get_permission_emails((
        'daiquiri_contact.view_contactmessage',
    )) + get_admin_emails()


def send_contact_message(request, message):
    # sends an email to the admins, managers and the user once a message was submitted.
    context = {
        'user': message.user,
        'author': message.author,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
        'url': request.build_absolute_uri(reverse('contact:messages'))
    }
    send_mail(request, 'contact/email/new_message_admin', context, get_manager_emails())
    send_mail(request, 'contact/email/new_message_user', context, [message.email])
