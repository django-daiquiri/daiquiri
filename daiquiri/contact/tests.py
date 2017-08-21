from test_generator.viewsets import TestModelViewsetMixin

from daiquiri.core.tests import TestCase

from .models import ContactMessage


class ContactTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'contact.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_view': {
            'admin': 200, 'user': 403, 'anonymous': 302
        },
        'list_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'retrieve_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 201, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 204, 'user': 403, 'anonymous': 403
        },
        'user_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 403
        }
    }

class MessagesTests(TestModelViewsetMixin, ContactTestCase):

    instances = ContactMessage.objects.all()
    url_names = {
        'viewset': 'contact:message'
    }

