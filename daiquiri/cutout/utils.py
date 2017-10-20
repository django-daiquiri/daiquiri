from django.conf import settings

from daiquiri.core.utils import import_class

def get_adapter():
    return import_class(settings.CUTOUT_ADAPTER)()
