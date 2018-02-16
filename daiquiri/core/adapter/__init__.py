from django.conf import settings

from daiquiri.core.utils import import_class


def DatabaseAdapter():
    return import_class(settings.ADAPTER_DATABASE)('data', settings.DATABASES['data'])


def DownloadAdapter():
    return import_class(settings.ADAPTER_DOWNLOAD)('data', settings.DATABASES['data'])
