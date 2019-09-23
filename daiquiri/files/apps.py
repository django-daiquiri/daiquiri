from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class FilesConfig(AppConfig):
    name = 'daiquiri.files'
    label = 'daiquiri_files'
    verbose_name = 'Files'

    def ready(self):
        if not settings.FILES_BASE_PATH:
            raise ImproperlyConfigured('FILES_BASE_PATH is not set')
