from django.core.urlresolvers import reverse

from test_generator.viewsets import TestModelViewsetMixin

from daiquiri.core.tests import TestCase

from .models import Example


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


class TestUserViewsetMixin(object):

    def _test_user_viewset(self, username):

        url = reverse(self.url_names['viewset'] + '-user')
        response = self.client.get(url, self.get_list_viewset_query_params())

        self.assertEqual(response.status_code, self.status_map['user_viewset'][username], msg=(
            ('username', username),
            ('url', url),
            ('status_code', response.status_code),
            ('content', response.content)
        ))


class ExampleTests(TestUserViewsetMixin, TestModelViewsetMixin, QueryTestCase):

    instances = Example.objects.all()
    url_names = {
        'viewset': 'query:example'
    }
