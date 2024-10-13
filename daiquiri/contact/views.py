from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import TemplateView

from daiquiri.core.views import CSRFViewMixin, ModelPermissionMixin, StoreIdViewMixin

from .forms import ContactForm
from .utils import send_contact_message


@login_required()
def contact(request):
    contact_form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return render(request, 'core/home.html')

        if contact_form.is_valid():

            message = contact_form.save(commit=False)
            message.set_status_active()
            message.created = now()

            message.user = request.user
            message.email = request.user.email
            message.author = request.user.profile.full_name

            message.save()

            send_contact_message(request, message)

            return render(request, 'contact/thanks.html')

    else:
        if request.user.is_authenticated:
            try:
                contact_form.initial = {
                    'email': request.user.email,
                    'author': request.user.profile.full_name
                }
            except AttributeError:
                pass

    return render(request, 'contact/contact.html', {'form': contact_form})


class MessagesView(ModelPermissionMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):
    template_name = 'contact/messages.html'
    permission_required = 'daiquiri_contact.view_contactmessage'
