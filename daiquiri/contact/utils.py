from django.urls import reverse

from daiquiri.core.utils import send_mail, get_admin_emails


def send_contact_message(request, message):

    admin_emails = get_admin_emails()
    context = {
        'user': message.user,
        'author': message.author,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
        'url': request.build_absolute_uri(reverse('contact:messages'))
    }
    send_mail(request, 'contact/email/new_message_admin', context, admin_emails)
    send_mail(request, 'contact/email/new_message_user', context, [message.email])
