from django.shortcuts import render
from django.utils.timezone import now

from .forms import ContactForm
from .utils import send_contact_message


def contact(request):
    contact_form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return render(request, 'core/home.html')

        if contact_form.is_valid():

            message = contact_form.save(commit=False)
            message.set_status_active()
            message.created = now()

            if request.user.is_authenticated:
                message.user = request.user

            message.save()

            send_contact_message(request, message)

            return render(request, 'contact/thanks.html')

    else:
        if request.user.is_authenticated:

            contact_form.initial = {
                'email': request.user.email,
                'name': request.user.profile.full_name
            }

    return render(request, 'contact/contact.html', {'form': contact_form})
