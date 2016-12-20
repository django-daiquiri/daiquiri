from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User

# from daiquiri_core.utils import send_mail
from .models import ContactMessage
from .forms import ContactForm

def get_admin_emails():
    return [user.email for user in User.objects.filter(is_superuser=True)]


def send_contact_message(request, contact_form):
        new_message = ContactMessage()

        new_message.name = request.POST.get('name', '')
        new_message.subject = request.POST.get('subject', '')
        new_message.email = request.POST.get('email', '')
        new_message.message = request.POST.get('message', '')
        new_message.set_status_active()

        new_message.save()


        site = get_current_site(request)

        subject = "[%s] %s" % (site.name, new_message.subject)

        from_email = settings.DEFAULT_FROM_EMAIL
        # send message to the admins
        admin_emails = get_admin_emails()
        msg_admin = EmailMessage(subject, new_message.message, from_email, admin_emails)
        msg_admin.send()

        # send confirmation message to the user
        user_email = "[%s]" % (new_message.email)
        msg_user = EmailMessage(subject, new_message.message, from_email, [user_email])
        msg_user.send()



