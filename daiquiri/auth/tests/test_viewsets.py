from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission

from test_generator.viewsets import TestListViewsetMixin, TestDetailViewsetMixin, TestUpdateViewsetMixin

from ..models import Profile


class AuthViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    def setUp(self):
        group = Group.objects.get(name='managers')
        for codename in (
            'add_profile',
            'change_profile',
            'delete_profile',
            'view_profile'
        ):
            group.permissions.add(Permission.objects.get(codename=codename))


class ProfileTests(TestListViewsetMixin, TestDetailViewsetMixin, TestUpdateViewsetMixin, AuthViewsetTestCase):

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
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'confirm_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'reject_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'activate_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'disable_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'enable_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
    }

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

    def _test_confirm_viewset(self, username):
        instance = User.objects.get(username='user')
        instance.profile.is_pending = True
        instance.save()

        self.assert_viewset('confirm_viewset', 'put', 'confirm', username, kwargs={
            'pk': instance.pk
        })

    def _test_reject_viewset(self, username):
        instance = User.objects.get(username='user')
        instance.profile.is_pending = True
        instance.save()

        self.assert_viewset('reject_viewset', 'put', 'reject', username, kwargs={
            'pk': instance.pk
        })

    def _test_activate_viewset(self, username):
        instance = User.objects.get(username='user')
        instance.profile.is_pending = True
        instance.profile.is_confirmed = True
        instance.save()

        self.assert_viewset('activate_viewset', 'put', 'activate', username, kwargs={
            'pk': instance.pk
        })

    def _test_disable_viewset(self, username):
        instance = User.objects.get(username='user')

        self.assert_viewset('disable_viewset', 'put', 'disable', username, kwargs={
            'pk': instance.pk
        })

    def _test_enable_viewset(self, username):
        instance = User.objects.get(username='user')
        instance.is_active = False
        instance.save()

        self.assert_viewset('enable_viewset', 'put', 'enable', username, kwargs={
            'pk': instance.pk
        })


class GroupViewSet(TestListViewsetMixin, TestDetailViewsetMixin, AuthViewsetTestCase):

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None)
    )

    instances = Group.objects.all()
    url_names = {
        'viewset': 'auth:group'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        }
    }
