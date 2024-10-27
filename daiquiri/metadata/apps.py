from django.apps import AppConfig


class MetadataConfig(AppConfig):
    name = 'daiquiri.metadata'
    label = 'daiquiri_metadata'
    verbose_name = 'Metadata'

    def ready(self):
        from . import handlers  # noqa: F401
