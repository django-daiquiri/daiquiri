from django.utils.deprecation import MiddlewareMixin


class MultipleProxyMiddleware(MiddlewareMixin):
    """
    see also: https://docs.djangoproject.com/en/2.1/ref/request-response/
    (but using the left most entry)
    """

    FORWARDED_FOR_FIELDS = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED_HOST',
        'HTTP_X_FORWARDED_SERVER',
    ]

    def process_request(self, request):
        """
        Rewrites the proxy headers so that only the most recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                request.META[field] = request.META[field].split(',')[0].strip()
