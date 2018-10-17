import logging
import os
import subprocess

from sendfile import sendfile

from django.conf import settings
from django.utils.timezone import now

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .models import Directory

logger = logging.getLogger(__name__)


def find_files(base_path, path, file_name):
    args = ['find', path, '-type', 'f', '-name', file_name]
    logger.debug('`%s`', ' '.join(args))

    try:
        output = subprocess.check_output(args, cwd=base_path)
        files = output.decode().split()
        return files
    except subprocess.CalledProcessError:
        return []


def check_file(user, file_path):
    # loop over all directories beginning with the hights depth and return as soon as a directory matches
    for directory in Directory.objects.order_by('-depth'):
        if os.path.normpath(file_path).startswith(directory.path):
            return Directory.objects.filter_by_access_level(user).filter(pk=directory.pk).exists()


def search_file(file_name, directory_path=None):
    base_path = os.path.normpath(settings.FILES_BASE_PATH)
    logger.debug('base_path = %s', base_path)

    if directory_path:
        try:
            directory = Directory.objects.get(path=directory_path)
            files = find_files(base_path, directory.path, file_name)
        except Directory.DoesNotExist:
            return None
    else:
        files = []
        for directory in Directory.objects.order_by('-depth'):
            files += find_files(base_path, directory.path, file_name)

    if len(files) == 1:
        # subtract the base path and return
        file_path = files.pop()

        logger.debug('file_name = %s found at %s', file_name, file_path)
        return file_path
    elif len(files) > 1:
        logger.debug('file_name = %s found more than once', file_name)
        return None
    else:
        logger.debug('file_name = %s not found', file_name)
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
