import logging
import os

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, reverse
from django.views.generic import View

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .search import Searcher
from .storage import FileStore
from .utils import (
    get_directory,
    is_cli_request,
    render_with_layout,
    resolve_content_path,
    resolve_resource_path,
    send_file,
)

logger = logging.getLogger(__name__)


class FileView(View):

    root = None

    def get(self, request, file_path, **kwargs):

        if not request.user.is_authenticated:
            try:
                credentials = TokenAuthentication().authenticate(request)
                if credentials is not None:
                    request.user = credentials[0]
            except AuthenticationFailed:
                return HttpResponse(
                    b"Invalid or missing authentication token.",
                    status=401,
                    content_type='text/plain'
                )

        if self.root:
            logger.debug('root=%s', self.root)
            file_path = os.path.join(self.root, file_path)

        store = FileStore()
        try:
            _ = store.path(file_path)
        except ValueError as err:
            logger.debug('%s not found: %s', file_path, err)
            raise Http404 from None

        requested_directory = get_directory(request.user, file_path)
        if requested_directory is None:
            logger.debug('%s is forbidden', file_path)
            if is_cli_request(request):
                return HttpResponseForbidden()
            if request.user.is_authenticated:
                raise PermissionDenied
            else:
                return redirect_to_login(request.path_info)

        if requested_directory.layout:
            resolved_path = resolve_content_path(store, file_path)
        else:
            resolved_path = resolve_resource_path(store, file_path)

        if resolved_path is None:
            logger.debug('%s not found', file_path)
            raise Http404

        if requested_directory.layout:
            return render_with_layout(request, store, resolved_path)

        filesystem_path = store.path(resolved_path)
        if filesystem_path.is_dir():
            entries = []
            RENDERED_FILETYPE_EXTENSIONS = {
                "aac", "ai", "bmp", "cs", "css", "csv", "doc", "docx", "exe", "gif", "heic",
                "html", "java", "jpg", "js", "json", "jsx", "key", "m4p", "md", "mdx", "mov",
                "mp3", "mp4", "otf", "pdf", "php", "png", "ppt", "pptx", "psd", "py", "raw",
                "rb", "sass", "scss", "sh", "sql", "svg", "tiff", "tsx", "ttf", "txt", "wav",
                "woff", "xls", "xlsx", "xml", "yml",
            }

            for child in sorted(filesystem_path.iterdir(), key=lambda item: item.name.casefold()):
                child_path = store.relative(child)

                if get_directory(request.user, child_path) is None:
                    continue

                extension = child.suffix[1:] if child.is_file() else None
                entries.append({
                    'name': child.name,
                    'extension': extension if extension in RENDERED_FILETYPE_EXTENSIONS else None,
                    'url': reverse('files:file', kwargs={'file_path': child_path}),
                    'is_dir': child.is_dir(),
                    'size': None if child.is_dir() else child.stat().st_size,
                })

            return render(request, 'files/directory.html', {'directory': entries})

        return send_file(request, store, resolved_path)


class SearchView(View):

    root = None

    def get(self, request, **kwargs):

        search_string = request.GET.get("q", "")

        results = Searcher.search_for_string(string_query=search_string)

        paginator = Paginator(results, settings.FILES_SEARCH_RESULTS_PER_PAGE)
        page_number = request.GET.get('page')
        search_results = paginator.get_page(page_number)

        context = {
                "search_results": search_results,
                "search_string": search_string,
                "num_of_search_results": len(results)
                }

        return render(request, "files/search-results.html", context)
