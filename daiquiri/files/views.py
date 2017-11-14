import logging

from sendfile import sendfile

from django.http import Http404
from django.utils.timezone import now

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import get_file

logger = logging.getLogger(__name__)


def file(request, file_path):
    if not file_path:
        raise Http404

    file_name = get_file(request.user, file_path)

    if file_name:
        # create a stats record for this job
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
        return sendfile(request, file_name, attachment=False)

    # if nothing worked, return 404
    raise Http404
