import logging
import os

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import View

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .search import Searcher
from .storage import FileStore
from .utils import (
    get_directory,
    is_cli_request,
    render_directory_listing,
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
            if resolved_path.endswith('.md') or resolved_path.endswith('.html'):
                return render_with_layout(request, store, resolved_path)
        else:
            if store.path(resolved_path).is_dir():
                return render_directory_listing(request, store, resolved_path)

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
