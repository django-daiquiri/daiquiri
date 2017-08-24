from django.test import TestCase

from test_generator.viewsets import TestModelViewsetMixin

from ..models import Example


class QueryTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'examples.json'
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


class ExampleTests(TestModelViewsetMixin, QueryTestCase):

    instances = Example.objects.all()
    url_names = {
        'viewset': 'query:example'
    }

    def _test_user_viewset(self, username):
        self.assert_list_viewset(username, list_route='user')
