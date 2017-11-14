from sendfile import sendfile

from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import search_file


class FileViewSet(viewsets.GenericViewSet):

    def list(self, request):

        search = request.GET.get('search', None)

        if search:
            file_name = search_file(request.user, search)

            if file_name:
                # create a stats record for this job
                Record.objects.create(
                    resource_type='FILE',
                    resource={
                        'file_name': file_name
                    },
                    client_ip=get_client_ip(request),
                    user=request.user
                )

                # send the file to the client
                return sendfile(request, file_name, attachment=False)
            else:
                raise NotFound()

        else:
            raise NotFound()
