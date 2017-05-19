from django.test import TestCase

from daiquiri.core.tests import (
    TestListViewMixin,
    TestModelStringMixin
)


from .models import Profile


class AuthTestCase(TestCase):
    fixtures = ['auth/testing.json']


class ProfileTests(TestListViewMixin,
                   TestModelStringMixin,
                   AuthTestCase):

    list_url_name = 'users'

    def setUp(self):
        self.client.login(username='admin', password='admin')
        self.instance = Profile.objects.get(user__username='user')
