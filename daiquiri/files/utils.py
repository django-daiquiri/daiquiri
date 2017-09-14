import os

from .models import Directory


def get_file(user, file_path):
    # append 'index.html' when the file_path is a directory
    if file_path.endswith('/'):
        file_path += 'index.html'

    # get directories this user has access to
    directories = Directory.objects.filter_by_access_level(user)

    results = set()
    for directory in directories:
        # normalize the file path so that /a/b/c and b/c/d/e become /a/b/c and d/e
        normalized_file_path = normalize_file_path(directory.path, file_path)

        # join directory_path and file_path so that it becomes /a/b/c/d/e
        absolute_file_path = os.path.join(directory.path, normalized_file_path)

        # check if absolute_file_path is actually a file
        if os.path.isfile(absolute_file_path):
            results.add(absolute_file_path)

    # check if we found the file more than once
    if len(results) > 1:
        raise Exception('More than one file found in %s.get_file().' % __name__)
    elif len(results) == 1:
        return results.pop()
    else:
        return None


def search_file(user, file_path):
    # get directories this user has access to
    directories = Directory.objects.filter_by_access_level(user)

    results = set()
    for directory in directories:
        for directory_path, dirs, files in os.walk(directory.path):
            # normalize the file path so that /a/b/c and b/c/d/e become /a/b/c and d/e
            normalized_file_path = normalize_file_path(directory_path, file_path)

            # join directory_path and file_path so that it becomes /a/b/c/d/e
            absolute_file_path = os.path.join(directory_path, normalized_file_path)

            # check if absolute_file_path is actually a file
            if os.path.isfile(absolute_file_path):
                results.add(absolute_file_path)

    # check if we found the file more than once
    if len(results) > 1:
        raise Exception('More than one file found in %s.get_file().' % __name__)
    elif len(results) == 1:
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
