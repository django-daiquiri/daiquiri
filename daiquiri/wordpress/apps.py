from django.apps import AppConfig


class WordpressConfig(AppConfig):
    name = 'daiquiri.wordpress'
    label = 'daiquiri_wordpress'
    verbose_name = 'Wordpress'

    def ready(self):
        from . import handlers
        from . import rules
