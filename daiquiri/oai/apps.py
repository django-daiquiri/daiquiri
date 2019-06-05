from django.apps import AppConfig


class OaiConfig(AppConfig):
    name = 'daiquiri.oai'
    label = 'daiquiri_oai'
    verbose_name = 'Oai'

    def ready(self):
        from . import handlers
