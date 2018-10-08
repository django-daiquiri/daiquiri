import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .utils import check_file, search_file, send_file

logger = logging.getLogger(__name__)


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)
        path = request.GET.get('path', None)

        logger.debug('search = "%s"', search)
        logger.debug('path = "%s"', path)

        if search:
            file_path = search_file(search, path)
            logger.debug('file_path = "%s"', file_path)

            if file_path is None:
                raise NotFound()

            has_permission = check_file(request.user, file_path)
            logger.debug('has_permission = "%s"', has_permission)

            if has_permission is None:
                raise NotFound()

            if request.GET.get('download', True):
                return send_file(request, file_path, search)
            else:
                # send an empty response
                return Response()

        else:
            raise ValidationError({
                'search': [_('This field may not be blank.')]
            })
