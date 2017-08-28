from django.test import TestCase

from test_generator.views import TestListViewMixin


class ContactViewTestCase(TestCase):

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
        }
    }


class MessagesTests(TestListViewMixin, ContactViewTestCase):

    url_names = {
        'list_view': 'messages'
    }
