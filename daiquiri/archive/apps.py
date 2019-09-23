from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class ArchiveConfig(AppConfig):
    name = 'daiquiri.archive'
    label = 'daiquiri_archive'
    verbose_name = 'Archive'

    def ready(self):
        if not settings.ARCHIVE_BASE_PATH:
            raise ImproperlyConfigured('ARCHIVE_BASE_PATH is not set')
        if not settings.ARCHIVE_DOWNLOAD_DIR:
            raise ImproperlyConfigured('ARCHIVE_DOWNLOAD_DIR is not set')
