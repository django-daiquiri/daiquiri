from django.apps import AppConfig


class QueryConfig(AppConfig):
    name = 'daiquiri.query'
    label = 'daiquiri_query'
    verbose_name = 'Query'

    def ready(self):
        from . import handlers
