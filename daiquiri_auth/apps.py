from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'daiquiri_auth'
    verbose_name = 'Daiquiri Auth'

    def ready(self):
        from . import handlers
