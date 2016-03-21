from django.test import TestCase

from daiquiri_core.tests import TestListViewMixin
from daiquiri_core.tests import TestRetrieveViewMixin
from daiquiri_core.tests import TestCreateViewMixin
from daiquiri_core.tests import TestUpdateViewMixin
from daiquiri_core.tests import TestDeleteViewMixin
from daiquiri_core.tests import TestModelStringMixin

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
