import warnings

from django.apps import AppConfig
from django.conf import settings


class DatalinkConfig(AppConfig):
    name = 'daiquiri.datalink'
    label = 'daiquiri_datalink'
    verbose_name = 'Datalink'

    def ready(self):
        if settings.DATALINK_ADAPTER:
            warnings.warn(
                'DATALINK_ADAPTER is deprecated and overrides the / adapter in '
                f'DATALINK_SERVICES: {settings.DATALINK_ADAPTER}. See '
                'https://django-daiquiri.github.io/docs/settings/#datalink_adapter',
                FutureWarning,
                stacklevel=2,
            )
