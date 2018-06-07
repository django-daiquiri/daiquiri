from django.contrib.auth.models import User
from django.test import TestCase

from test_generator.viewsets import (
    TestModelViewsetMixin,
    TestListViewsetMixin,
    TestViewsetMixin,
    TestDetailViewsetMixin,
    TestUpdateViewsetMixin,
    TestDeleteViewsetMixin,
)

from daiquiri.core.utils import setup_group

from ..models import Meeting, Participant, Contribution


class MeetingsViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
        'meetings.json'
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    def setUp(self):
        group, created = setup_group('meetings_manager')
        User.objects.get(username='manager').groups.add(group)


class MeetingTests(TestModelViewsetMixin, MeetingsViewsetTestCase):

    status_map = {
        'list_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 405, 'manager': 405, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 405, 'manager': 405, 'user': 403, 'anonymous': 403
        }
    }

    instances = Meeting.objects.all()
    url_names = {
        'viewset': 'meetings:meeting'
    }


class ParticipantTests(TestListViewsetMixin,
                       TestDetailViewsetMixin,
                       TestUpdateViewsetMixin,
                       TestDeleteViewsetMixin,
                       MeetingsViewsetTestCase):

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
            'admin': 405, 'manager': 405, 'user': 403, 'anonymous': 403
        }
    }

    instances = Participant.objects.all()
    url_names = {
        'viewset': 'meetings:participant'
    }


class ContributionTests(TestModelViewsetMixin, MeetingsViewsetTestCase):

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
            'admin': 405, 'manager': 405, 'user': 403, 'anonymous': 403
        }
    }

    instances = Contribution.objects.all()
    url_names = {
        'viewset': 'meetings:contribution'
    }
