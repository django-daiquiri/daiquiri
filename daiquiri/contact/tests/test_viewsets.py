from django.test import TestCase

from test_generator.viewsets import TestModelViewsetMixin

from ..models import ContactMessage


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
        'list_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
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
