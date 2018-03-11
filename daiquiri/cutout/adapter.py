from django.conf import settings

from daiquiri.core.utils import import_class


def CutOutAdapter():
    return import_class(settings.CUTOUT_ADAPTER)()


class BaseCutOutAdapter(object):

    def clean(self, request, resource):
        raise NotImplementedError()

    def stream(self):
        raise NotImplementedError()
