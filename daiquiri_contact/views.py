from django.shortcuts import render

from .forms import ContactForm
from .utils import send_contact_message
from datetime import datetime



def contact(request):
    contact_form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return render(request, 'core/home.html')

        if contact_form.is_valid():

            new_message = contact_form.save(commit=False)
            new_message.set_status_active()
            new_message.datetime = datetime.now()

            if request.user.is_authenticated:
                new_message.User = request.user

            new_message.save()

            send_contact_message(request, new_message)

            return render(request, 'contact/thanks.html')

    else:
        if request.user.is_authenticated:

            contact_form.initial = {
                'email': request.user.email,
                'name': request.user.profile.full_name
            }

    return render(request, 'contact/contact.html', {'form': contact_form})





