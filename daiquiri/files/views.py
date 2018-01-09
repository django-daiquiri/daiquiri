import os

from sendfile import sendfile

from django.conf import settings
from django.http import Http404
from django.utils.timezone import now

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import check_file


def file(request, file_path):
    if not file_path:
        raise Http404

    # append 'index.html' when the file_path is a directory
    if file_path.endswith('/'):
        file_path += 'index.html'

    # get the absolute path to the file
    absolute_file_path = os.path.join(settings.FILES_BASE_PATH, file_path)

    if check_file(request.user, absolute_file_path):
        # create a stats record for this job
        Record.objects.create(
            time=now(),
            resource_type='FILE',
            resource={
                'file_path': file_path,
                'absolute_file_path': absolute_file_path
            },
            client_ip=get_client_ip(request),
            user=request.user
        )

        # send the file to the client
        return sendfile(request, absolute_file_path, attachment=False)

    # if nothing worked, return 404
    raise Http404
