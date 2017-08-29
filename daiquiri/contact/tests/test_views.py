from django.test import TestCase

from test_generator.views import TestViewMixin, TestListViewMixin


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
        'list_view': 'contact:messages'
    }


class ContactTests(TestViewMixin, ContactViewTestCase):

    url_names = {
        'create_view': 'contact:contact'
    }

    status_map = {
        'create_view_get': {
            'admin': 200, 'user': 200, 'anonymous': 200
        },
        'create_view_post': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_contact_get(self, username):
        self.assert_view('create_view_get', 'get', 'create_view', username)

    def _test_contact_post(self, username):
        self.assert_view('create_view_post', 'post', 'create_view', username, data={
            'author': 'Tom Test',
            'email': 'test@example.com',
            'subject': 'This is a test',
            'message': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est. Lorem ipsum dolor sit amet.'
        })

    def _test_contact_post_invalid(self, username):
        self.assert_view('create_view_post', 'post', 'create_view', username, data={})

    def _test_contact_cancel(self, username):
        self.assert_view('create_view_post', 'post', 'create_view', username, data={
            'cancel': True
        })
