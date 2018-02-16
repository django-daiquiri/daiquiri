from django.conf import settings

from daiquiri.core.utils import import_class

def Adapter():
    return import_class(settings.CUTOUT_ADAPTER)()
