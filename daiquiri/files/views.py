from django.http import Http404
from django.views.generic import View

from .utils import check_file, send_file


class FileView(View):

    def get(self, request, file_path):
        # append 'index.html' when the file_path is a directory
        if not file_path or file_path.endswith('/'):
            file_path += 'index.html'

        if check_file(request.user, file_path):
            return send_file(request, file_path)

        # if nothing worked, return 404
        raise Http404
