from django.test import TestCase
from django.contrib.auth.models import Group

from test_generator.viewsets import TestListViewsetMixin, TestDetailViewsetMixin, TestUpdateViewsetMixin

from ..models import Profile


class AuthTestCase(TestCase):

    fixtures = (
        'auth.json',
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
        'detail_viewset': {
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


class ProfileTests(TestListViewsetMixin, TestDetailViewsetMixin, TestUpdateViewsetMixin, AuthTestCase):

    instances = Profile.objects.all()
    url_names = {
        'viewset': 'auth:profile'
    }

    def _test_update_viewset(self, username):
        for instance in self.instances:
            instance.details = {}

            data = self.get_instance_as_dict(instance)
            data['user'] = {
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'groups': [group.id for group in instance.user.groups.all()]
            }

            self.assert_update_viewset(username, kwargs={
                'pk': instance.pk
            }, data=data)


class GroupViewSet(TestListViewsetMixin, TestDetailViewsetMixin, AuthTestCase):

    instances = Group.objects.all()
    url_names = {
        'viewset': 'auth:group'
    }
