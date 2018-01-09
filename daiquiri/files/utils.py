import os

from django.conf import settings

from .models import Directory


def check_file(user, absolute_file_path):
    if not os.path.isfile(absolute_file_path):
        return False

    # loop over all directories beginning with the hights depth and return as soon as a directory matches
    for directory in Directory.objects.order_by('-depth'):
        if os.path.normpath(absolute_file_path).startswith(directory.absolute_path):
            return Directory.objects.filter_by_access_level(user).filter(pk=directory.pk).exists()


def search_file(user, search_path):
    base_path = os.path.normpath(settings.FILES_BASE_PATH)

    # look for the file in all directory below the base path
    results = set()
    for directory_path, _, _ in os.walk(base_path):
        normalized_file_path = normalize_file_path(directory_path, search_path)
        absolute_file_path = os.path.join(directory_path, normalized_file_path)

        if os.path.isfile(absolute_file_path):
            results.add(absolute_file_path)

    if len(results) == 1:
        return results.pop()
    else:
        return None


def normalize_file_path(directory_path, file_path):

    directory_path_tokens = os.path.normpath(directory_path).split(os.path.sep)
    file_path_tokens = os.path.normpath(file_path).split(os.path.sep)

    match = 0
    for i in range(len(file_path_tokens)):
        if file_path_tokens[:i] == directory_path_tokens[-i:]:
            match = i

    return os.path.join(*file_path_tokens[match:])
