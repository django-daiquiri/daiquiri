import logging

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import View

from .utils import get_directory, get_file_path, render_with_layout, send_file

logger = logging.getLogger(__name__)


class FileView(View):

    root = None

    def get(self, request, file_path, **kwargs):
        if self.root:
            logger.debug('root=%s', self.root)
            file_path = self.root.strip('/') + '/' + file_path

        file_path = get_file_path(file_path)
        if file_path is None:
            logger.debug('%s not found', file_path)
            raise Http404

        directory = get_directory(request.user, file_path)
        if directory is None:
            logger.debug('%s if forbidden', file_path)
            if request.user.is_authenticated:
                raise PermissionDenied
            else:
                return redirect_to_login(request.path_info)

        if file_path.endswith('.html') or file_path.endswith('.md') and directory.layout:
            return render_with_layout(request, file_path)
        else:
            return send_file(request, file_path)
