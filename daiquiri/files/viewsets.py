import os

from sendfile import sendfile

from django.conf import settings
from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import check_file, search_file


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)

        if search:
            file_path = search_file(search)

            if file_path and check_file(request.user, file_path):

                if request.GET.get('download', True):
                    # create a stats record for this download
                    Record.objects.create(
                        time=now(),
                        resource_type='FILE',
                        resource={
                            'search': search,
                            'file_path': file_path
                        },
                        client_ip=get_client_ip(request),
                        user=request.user
                    )

                    # send the file to the client
                    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)
                    return sendfile(request, absolute_file_path, attachment=True)
                else:
                    # send an empty response
                    return Response()
            else:
                raise NotFound()

        else:
            raise NotFound()
