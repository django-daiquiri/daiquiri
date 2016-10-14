from django.conf import settings


def get_query_backend():
    if 'backend' in settings.QUERY:
        if settings.QUERY['backend'] == 'direct':
            from .direct import DirectQueryBackend
            return DirectQueryBackend()
        else:
            raise Exception('query backend "%s" is not supported (yet)' % settings.QUERY['backend'])
    else:
        raise Exception('no query backend found in settings.QUERY')
