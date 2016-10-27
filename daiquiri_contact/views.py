from django.shortcuts import render

from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect

from forms import ContactForm

def contact(request):
    form_class = ContactForm

    # new logic!
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
        'form': form_class,
    })
