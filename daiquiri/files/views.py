import logging

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import View

from .utils import file_exists, check_file, send_file

logger = logging.getLogger(__name__)


class FileView(View):

    def get(self, request, file_path):
        # append 'index.html' when the file_path is a directory
        if not file_path or file_path.endswith('/'):
            file_path += 'index.html'

        if not file_exists(file_path):
            logger.debug('%s not found', file_path)
            raise Http404

        if check_file(request.user, file_path):
            return send_file(request, file_path)
        else:
            logger.debug('%s if forbidden', file_path)
            if request.user.is_authenticated:
                raise PermissionDenied
            else:
                return redirect_to_login(request.path_info)

        # if nothing worked, return 404
        raise Http404
