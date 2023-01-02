import os
import logging

from lunr import lunr

from django.conf import settings
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from django_sendfile import sendfile

from daiquiri.core.utils import get_client_ip, markdown
from daiquiri.stats.models import Record

from .models import Directory

logger = logging.getLogger(__name__)

# lunr index variable
_lunr_index = []

# content from all files
_cms_files = {}

def file_exists(file_path):
    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)
    return os.path.isfile(absolute_file_path)


def get_file_path(file_path):
    if file_exists(file_path):
        return file_path
    elif not file_path or file_path.endswith('/'):
        # try different paths
        for path in [file_path.rstrip('/') + '.html',
                     file_path.rstrip('/') + '.md',
                     file_path + 'index.html',
                     file_path + 'index.md']:
            if file_exists(path):
                return path

    # return None if no file was found
    return None


def get_directory(user, file_path):
    # loop over all directories beginning with the hights depth and return as soon as a directory matches
    for directory in Directory.objects.order_by('-depth'):
        if os.path.normpath(file_path).startswith(directory.path):
            try:
                return Directory.objects.filter_by_access_level(user).get(pk=directory.pk)
            except Directory.DoesNotExist:
                return None


def check_file(user, file_path):
    return get_directory(user, file_path) is not None


def render_with_layout(request, file_path):

    context = {}
    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)
    content = read_file_content(absolute_file_path)
    if content:
        context["content"] = content

    return render(request, 'files/layout.html', context)


def read_file_content(abs_file_path):
    """ Reads the content of a html- or md-file and returns html
    """
    if abs_file_path.endswith('.html') or abs_file_path.endswith('.md'):
        with open(abs_file_path) as f:
            file_content = f.read()

            if abs_file_path.endswith('.html'):
                return mark_safe(file_content)
            elif abs_file_path.endswith('.md'):
                return mark_safe(force_str(markdown(file_content)))
    else:
        return ""


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
    return sendfile(request, absolute_file_path)


def build_lunr_index():

    global _lunr_index
    global _cms_files

    docs_path = os.path.join(settings.FILES_BASE_PATH, settings.FILES_DOCS_PATH)

    unique_files = set()
    for dir_path, _, files in os.walk(docs_path):
        for file in files:
            file_path = get_file_path(os.path.join(dir_path, file))
            if file_path and (file_path.endswith(".html") or file_path.endswith(".md")):
                unique_files.add(file_path)

    any_changes = False

    # clean up files that do not exist anymore
    for file_path in _cms_files:
        if file_path not in unique_files:
            any_changes = True
            _cms_files.pop(file_path)


    # read content of a file if it was modified since the last read
    for file_path in unique_files:
        current_mtime = os.path.getmtime(file_path)
        previous_mtime = _cms_files.get(file_path, {}).get("mtime", 0.0)
        if current_mtime != previous_mtime:
            any_changes = True
            _cms_files[file_path] = {}
            _cms_files[file_path]["mtime"] = current_mtime
            _cms_files[file_path]["body"] = read_file_content(file_path)
            _cms_files[file_path]["url"] = \
                    os.path.join(settings.FILES_BASE_URL,
                                 os.path.relpath(os.path.splitext(file_path)[0],
                                                 settings.FILES_BASE_PATH), "")

    # make an update of the lunr index if there were any changes in the files
    # since the previous search
    if any_changes:
        docs = [{
            "path": path,
            "url": doc["url"],
            "body": doc["body"]
            } for path, doc in _cms_files.items()]
        _lunr_index = lunr(ref="url", fields=("body",), documents = docs)

    return _lunr_index, _cms_files

