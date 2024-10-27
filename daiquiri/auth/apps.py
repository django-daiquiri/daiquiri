from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'daiquiri.auth'
    label = 'daiquiri_auth'
    verbose_name = 'User Profiles'

    def ready(self):
        from . import handlers  # noqa: F401
