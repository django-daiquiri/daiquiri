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
            contact_message = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            template = get_template('contact_template.txt')
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
                "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('contact/thanks')

    return render(request, 'contact/contact.html', {
        'form': form_class,
    })


def thanks(request):
    return HttpResponse('Thank you for your message! We will respond as soon as possible.')