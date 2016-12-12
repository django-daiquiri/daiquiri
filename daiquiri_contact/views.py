from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import detail_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

#from daiquiri_core.permissions import DaiquiriModelPermissions
#from daiquiri_core.utils import get_referer_url_name, get_next_redirect

from .models import ContactMessage
from .forms import ContactForm

from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect



def contact(request):

    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)

        if form.is_valid():
            new_message = ContactMessage()
            new_message.name = request.POST.get('name', '')
            new_message.subject = request.POST.get('subject', '')
            new_message.email = request.POST.get('email', '')
            new_message.message = request.POST.get('message', '')

            # Email the profile with the
            # contact information
            template = get_template('contact/contact_template.txt')
            context = Context({
                'contact_name': new_message.name,
                'contact_email': new_message.email,
                'contact_subject': new_message.subject,
                'contact_message': new_message.message,
            })
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission",
                content,
                "example.com" +'',
                ['admin@example.com'],
                headers = {'Reply-To': new_message.email }
            )
            email.send()
            new_message.save()
            return render(request, 'contact/thanks.html')
        else:
            return HttpResponse('Make sure all fields are entered and valid.')

    return render(request, 'contact/contact.html', {
        'form': form,
    })
