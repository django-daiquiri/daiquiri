from sendfile import sendfile

from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import search_file


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)

        if search:
            file_name = search_file(request.user, search)

            if file_name:
                if request.GET.get('download', True):
                    # create a stats record for this download
                    Record.objects.create(
                        time=now(),
                        resource_type='FILE',
                        resource={
                            'file_name': file_name
                        },
                        client_ip=get_client_ip(request),
                        user=request.user
                    )

                    # send the file to the client
                    return sendfile(request, file_name, attachment=True)
                else:
                    # send an empty response
                    return Response()
            else:
                raise NotFound()

        else:
            raise NotFound()
