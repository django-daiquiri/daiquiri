from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User

from daiquiri_core.utils import send_mail
from .models import ContactMessage
from .forms import ContactForm

def get_admin_emails():
    return [user.email for user in User.objects.filter(is_superuser=True)]


def send_contact_message(request, new_message):

        emails = get_admin_emails()
        context = {
            'user': new_message.User,
            'name': new_message.name,
            'email': new_message.email,
            'subject': new_message.subject,
            'message': new_message.message,
        }
        send_mail(request, 'contact/email/new_message_admins', context, emails)
        send_mail(request, 'contact/email/new_message_user', context, [new_message.email])
