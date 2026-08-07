import logging
import os
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin
from warnings import deprecated

from django.apps import apps
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from django_sendfile import sendfile

from daiquiri.core.utils import get_client_ip, markdown

from .models import Directory
from .storage import FileStore

logger = logging.getLogger(__name__)


@deprecated((
    'This function is deprecated and will be removed in a future version. '
    'Use `FileStore.path` instead.'
))
def file_exists(file_path: str) -> bool:
    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)
    return os.path.isfile(absolute_file_path) or os.path.isdir(absolute_file_path)


def resolve_content_path(store: FileStore, requested_path: str) -> str | None:
    requested_path = requested_path.rstrip('/')
    filesystem_path = store.path(requested_path)

    if filesystem_path.is_file() and requested_path.endswith(('.html', '.md')):
        return requested_path

    for content_path in (
        requested_path + '.html',
        requested_path + '.md',
    ):
        if store.path(content_path).is_file():
            return content_path

    for index_name in settings.FILES_INDEX_NAMES:
        index_path = os.path.join(requested_path, index_name)
        if store.path(index_path).is_file():
            return index_path

    return None


def resolve_resource_path(store: FileStore, requested_path: str) -> str | None:
    requested_path = requested_path.rstrip('/')
    filesystem_path = store.path(requested_path)

    if filesystem_path.is_file() or filesystem_path.is_dir():
        return requested_path

    return None


@deprecated((
    'This function is deprecated and will be removed in a future version. '
    'Use `resolve_content_path` instead.'
))
def get_file_path(file_path: str) -> Path | str | None:
    if file_exists(file_path):
        return file_path
    elif not file_path or file_path.endswith('/'):
        # try different paths
        for path in [
            file_path.rstrip('/') + '.html',
            file_path.rstrip('/') + '.md',
            file_path + 'index.html',
            file_path + 'index.md',
        ]:
            if file_exists(path):
                return path

    # return None if no file was found
    return None


def get_directory(user, file_path: str):
    # loop over all directories beginning with the highest depth and
    # return as soon as a directory matches
    requested_path = PurePosixPath(file_path)
    for directory in Directory.objects.order_by('-depth'):
        directory_path = PurePosixPath(directory.path)
        try:
            _ = requested_path.relative_to(directory_path)
        except ValueError:
            continue

        try:
            return Directory.objects.filter_by_access_level(user).get(
                pk=directory.pk
            )
        except Directory.DoesNotExist:
            return None

    return None


@deprecated('This function is deprecated and will be removed in a future version.')
def check_file(user, file_path):
    return get_directory(user, file_path) is not None


def render_directory_listing(request, store: FileStore, file_path: str):
    filesystem_path = store.path(file_path)
    RENDERED_FILETYPE_EXTENSIONS = {
        "aac", "ai", "bmp", "cs", "css", "csv", "doc", "docx", "exe", "gif", "heic",
        "html", "java", "jpg", "js", "json", "jsx", "key", "m4p", "md", "mdx", "mov",
        "mp3", "mp4", "otf", "pdf", "php", "png", "ppt", "pptx", "psd", "py", "raw",
        "rb", "sass", "scss", "sh", "sql", "svg", "tiff", "tsx", "ttf", "txt", "wav",
        "woff", "xls", "xlsx", "xml", "yml",
    }

    directories = []
    files = []
    listing_truncated = False
    with os.scandir(filesystem_path) as scan:
        for child in scan:
            child_path = store.relative(Path(child.path))
            is_dir = child.is_dir()

            if not is_dir and not child.is_file():
                continue

            if is_dir:
                if get_directory(request.user, child_path) is None:
                    continue

            if len(directories) + len(files) >= settings.FILES_DIRECTORY_LISTING_MAX_ENTRIES:
                listing_truncated = True
                break

            entry = {
                'name': child.name,
                'extension': None,
                'url': reverse('files:file', kwargs={'file_path': child_path}),
                'is_dir': is_dir,
                'size': None,
            }

            if is_dir:
                directories.append(entry)
            else:
                extension = os.path.splitext(child.name)[1][1:].lower()
                entry['extension'] = extension if extension in RENDERED_FILETYPE_EXTENSIONS else None
                entry['size'] = child.stat().st_size
                files.append(entry)

    if directories:
        directories.sort(key=lambda entry: entry['name'].casefold())
    if files:
        files.sort(key=lambda entry: entry['name'].casefold())

    return render(request, 'files/directory.html', {
        'directory': directories + files,
        'listed_entries_count': len(directories) + len(files),
        'directory_listing_truncated': listing_truncated,
        'directory_listing_limit': settings.FILES_DIRECTORY_LISTING_MAX_ENTRIES,
        'breadcrumbs': get_breadcrumbs(file_path),
    })


def render_with_layout(request, store: FileStore, file_path: str):
    filesystem_path = store.path(file_path)
    content = read_file_content(filesystem_path)
    context = {'content': content } if content else {}
    return render(request, 'files/layout.html', context)


def get_breadcrumbs(file_path: str):
    breadcrumbs = []
    for parent in reversed(Path(file_path).parents):
        breadcrumbs.append({
            "name": parent.name,
            "url": reverse('files:file', kwargs={'file_path': parent.as_posix()}),
        })
    breadcrumbs.append({
        "name": Path(file_path).name,
        "url": reverse('files:file', kwargs={'file_path': file_path}),
    })
    return breadcrumbs


def read_file_content(filesystem_path: Path):
    """Reads the content of a html- or md-file and returns html"""
    if filesystem_path.suffix not in ('.html', '.md'):
        return ''

    with filesystem_path.open() as f:
        file_content = f.read()

    if filesystem_path.suffix == '.html':
        return mark_safe(file_content)
    return mark_safe(force_str(markdown(file_content)))



def send_file(request, store: FileStore, file_path: str, search=None):
    # create a stats record for this download
    resource = {'file_path': file_path}
    if search:
        resource['search'] = search

    filesystem_path = store.path(file_path)

    if apps.is_installed('daiquiri.stats'):
        from daiquiri.stats.models import Record
        Record.objects.create(
            time=now(),
            resource_type='FILE',
            resource=resource,
            client_ip=get_client_ip(request),
            user=request.user if request.user.is_authenticated else None,
            size=filesystem_path.stat().st_size if filesystem_path.is_file() else None
        )

    # send the file to the client
    return sendfile(request, str(filesystem_path))


@deprecated((
    'This function is deprecated and will be removed in a future version. '
    'Use reverse("files:file", kwargs={"file_path": file_path}) instead.'
))
def get_url_from_file_path(file_path: Path | str) -> str:
    url = urljoin(
        settings.FILES_BASE_URL,
        reverse(
            'files:file',
            kwargs={'file_path': file_path},
        ),
    )
    return url


@deprecated((
    'This function is deprecated and will be removed in a future version. '
    'Use `FileStore.path` instead.'
))
def make_file_path_absolute(file_path: Path | str) -> Path:
    res_path = Path(settings.FILES_BASE_PATH) / Path(file_path)
    return res_path


@deprecated('This function is deprecated and will be removed in a future version.')
def make_file_path_relative(file_path: Path | str) -> Path:
    res_path = Path(file_path).relative_to(settings.FILES_BASE_PATH)
    return res_path


def is_cli_request(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'wget' in user_agent or 'curl' in user_agent:
        return True
    return False

