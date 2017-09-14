import logging

from sendfile import sendfile

from django.http import Http404

from .utils import get_file

logger = logging.getLogger(__name__)


def file(request, file_path):

    file_name = get_file(request.user, file_path)

    if file_name:
        return sendfile(request, file_name, attachment=False)

    # if nothing worked, return 404
    raise Http404
