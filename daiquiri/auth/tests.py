from django.contrib.auth.models import User, Group

from test_generator.views import TestListViewMixin
from test_generator.viewsets import (
    TestListViewsetMixin,
    TestRetrieveViewsetMixin,
    TestUpdateViewsetMixin
)

from daiquiri.core.tests import TestCase

from .models import Profile


class AuthTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    languages = (
        'en',
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
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        }
    }


class UsersTests(TestListViewMixin, AuthTestCase):

    url_names = {
        'list_view': 'users'
    }


class ProfileTests(TestListViewsetMixin, TestRetrieveViewsetMixin, TestUpdateViewsetMixin, AuthTestCase):

    instances = Profile.objects.all()
    url_names = {
        'viewset': 'profile'
    }

    def prepare_update_instance(self, instance):
        instance.details = {}
        return instance

    def prepare_update_data(self, data):
        user = User.objects.get(pk=data['user'])
        groups = [group.id for group in user.groups.all()]

        data['user'] = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'groups': groups
        }

        return data


class GroupViewSet(TestListViewsetMixin, TestRetrieveViewsetMixin, AuthTestCase):

    instances = Group.objects.all()
    url_names = {
        'viewset': 'group'
    }
