from django.utils.deprecation import MiddlewareMixin
from daiquiri.query.utils import get_quota

class ChunkedTransferMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'HTTP_TRANSFER_ENCODING' in request.META \
                and request.META['HTTP_TRANSFER_ENCODING'] == 'chunked' \
                and request.path.startswith('/tap/'):
            upload_quota = get_quota(request.user, 'QUERY_UPLOAD_LIMIT')
            request.META["CONTENT_LENGTH"] = upload_quota
            request._stream.limit = upload_quota

