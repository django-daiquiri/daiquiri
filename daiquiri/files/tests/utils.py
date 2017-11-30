import os

from django.conf import settings
from django.contrib.auth.models import Group

from daiquiri.core.constants import ACCESS_LEVEL_INTERNAL, ACCESS_LEVEL_PRIVATE
from daiquiri.files.models import Directory


def setUp_directories():
    internal_directory = Directory(
        path=os.path.join(settings.BASE_DIR, 'files', 'html'),
        access_level=ACCESS_LEVEL_INTERNAL
    )
    internal_directory.save()

    private_directory = Directory(
        path=os.path.join(settings.BASE_DIR, 'files', 'images'),
        access_level=ACCESS_LEVEL_PRIVATE
    )
    private_directory.save()
    private_directory.groups.add(Group.objects.get(name='managers'))
    private_directory.save()
