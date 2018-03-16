from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .utils import check_file, search_file, send_file


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)

        if search:
            file_path = search_file(search)

            if file_path and check_file(request.user, file_path):

                if request.GET.get('download', True):
                    return send_file(request, file_path, search)
                else:
                    # send an empty response
                    return Response()
            else:
                raise NotFound()

        else:
            raise ValidationError({
                'search': [_('This field may not be blank.')]
            })
