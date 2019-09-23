from django.test import TestCase

from test_generator.viewsets import TestModelViewsetMixin

from ..models import ContactMessage

from daiquiri.core.utils import setup_group


class ContactTestCase(TestCase):

    fixtures = (
        'auth.json',
        'contact.json'
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 201, 'manager': 201, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 204, 'manager': 204, 'user': 403, 'anonymous': 403
        },
        'user_viewset': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 403
        }
    }

    def setUp(self):
        setup_group('contact_manager')


class MessagesTests(TestModelViewsetMixin, ContactTestCase):

    instances = ContactMessage.objects.all()
    url_names = {
        'viewset': 'contact:message'
    }
