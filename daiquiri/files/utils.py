import logging
import os

from sendfile import sendfile

from django.conf import settings
from django.utils.timezone import now

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .models import Directory

logger = logging.getLogger(__name__)


def check_file(user, file_path):
    # loop over all directories beginning with the hights depth and return as soon as a directory matches
    for directory in Directory.objects.order_by('-depth'):
        if os.path.normpath(file_path).startswith(directory.path):
            return Directory.objects.filter_by_access_level(user).filter(pk=directory.pk).exists()


def search_file(search_path):
    base_path = os.path.normpath(settings.FILES_BASE_PATH)

    # look for the file in all directory below the base path
    results = set()
    for directory_path, _, _ in os.walk(base_path):
        normalized_file_path = normalize_file_path(directory_path, search_path)
        absolute_file_path = os.path.join(directory_path, normalized_file_path)

        if os.path.isfile(absolute_file_path):
            results.add(absolute_file_path)

    if len(results) == 1:
        # subtract the base path and return
        file_path = results.pop().split(base_path, 1)[1].lstrip('/')

        logger.debug('%s => %s', search_path, file_path)
        return file_path
    elif len(results) > 1:
        logger.debug('search_path = %s found more than once', search_path)
        return None
    else:
        logger.debug('search_path = %s not found', search_path)
        return None


def send_file(request, file_path, search=None):
    # create a stats record for this download
    resource = {
        'file_path': file_path
    }
    if search:
        resource['search'] = search

    Record.objects.create(
        time=now(),
        resource_type='FILE',
        resource=resource,
        client_ip=get_client_ip(request),
        user=request.user if request.user.is_authenticated else None
    )

    # send the file to the client
    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)
    return sendfile(request, absolute_file_path, attachment=True)


def normalize_file_path(directory_path, file_path):

    directory_path_tokens = os.path.normpath(directory_path).split(os.path.sep)
    file_path_tokens = os.path.normpath(file_path).split(os.path.sep)

    match = 0
    for i in range(len(file_path_tokens)):
        if file_path_tokens[:i] == directory_path_tokens[-i:]:
            match = i

    return os.path.join(*file_path_tokens[match:])
