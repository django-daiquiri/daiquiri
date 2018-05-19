from django.conf import settings

from daiquiri.core.utils import import_class


def get_resolver():
    if settings.SERVE_RESOLVER:
        return import_class(settings.SERVE_RESOLVER)()
    else:
        return None
