from sendfile import sendfile

from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from .utils import search_file


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)

        if search:
            file_name = search_file(request.user, search)

            if file_name:
                return sendfile(request, file_name, attachment=False)
            else:
                raise NotFound()

        else:
            raise NotFound()
