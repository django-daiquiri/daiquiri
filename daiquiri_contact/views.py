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
            contact_name = request.POST.get('contact_name', '')
            contact_subject = request.POST.get('contact_subject', '')
            contact_email = request.POST.get('contact_email', '')
            contact_message = request.POST.get('contact_message', '')

            # Email the profile with the
            # contact information
            template = get_template('contact/contact_template.txt')
            context = Context({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'contact_subject': contact_subject,
                'contact_message': contact_message,
            })
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission",
                content,
                "example.com" +'',
                ['admin@example.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return render(request, 'contact/thanks.html')
        else:
            return HttpResponse('Make sure all fields are entered and valid.')

    return render(request, 'contact/contact.html', {
        'form': form,
    })
