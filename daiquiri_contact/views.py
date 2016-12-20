from django.shortcuts import render

from .forms import ContactForm
from .utils import send_contact_message


def contact(request):
    contact_form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return render(request, 'core/home.html')

        if contact_form.is_valid():

            send_contact_message(request, contact_form)

            return render(request, 'contact/thanks.html')

    return render(request, 'contact/contact.html', {'form': contact_form})





