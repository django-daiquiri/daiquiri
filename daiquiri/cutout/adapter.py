from django.conf import settings

from daiquiri.core.utils import import_class
from daiquiri.core.adapter.stream import BaseServiceAdapter


def CutOutAdapter():
    return import_class(settings.CUTOUT_ADAPTER)()


class BaseCutOutAdapter(BaseServiceAdapter):
    pass
