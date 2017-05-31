from django.shortcuts import render
from django.utils.timezone import now

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from daiquiri.core.views import ChoicesViewSet
from daiquiri.core.permissions import DaiquiriModelPermissions

from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .forms import ContactForm
from .utils import send_contact_message
from .paginations import MessagePagination


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
            try:
                contact_form.initial = {
                    'email': request.user.email,
                    'author': request.user.profile.full_name
                }
            except AttributeError:
                pass


    return render(request, 'contact/contact.html', {'form': contact_form})


def messages(request):
    # get urls to the admin interface to be used with angular
    return render(request, 'contact/messages.html', {})


class ContactMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (DaiquiriModelPermissions, )

    queryset = ContactMessage.objects.all()

    serializer_class = ContactMessageSerializer
    pagination_class = MessagePagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('author', 'email', 'subject', 'status')


class StatusViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ContactMessage.STATUS_CHOICES
