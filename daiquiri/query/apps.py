from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class QueryConfig(AppConfig):
    name = 'daiquiri.query'
    label = 'daiquiri_query'
    verbose_name = 'Query'

    def ready(self):
        if not settings.QUERY_DOWNLOAD_DIR:
            raise ImproperlyConfigured('QUERY_DOWNLOAD_DIR is not set')
        if not settings.QUERY_DOWNLOAD_DIR:
            raise ImproperlyConfigured('QUERY_UPLOAD_DIR is not set')

        from . import handlers  # noqa: F401
