from django.core.urlresolvers import reverse, resolve
from django.utils.six.moves.urllib.parse import urlparse


def get_script_alias(request):
    return request.path[:-len(request.path_info)]


def get_referer_path_info(request, default=None):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        return default

    script_alias = get_script_alias(request)
    return urlparse(referer).path[len(script_alias):]


def get_referer_url_name(request, default=None):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        return default

    referer_path = urlparse(referer).path
    referer_url_name = resolve(referer_path).url_name

    return referer_url_name


def get_internal_link(text, name, *args, **kwargs):

    if 'ng_args' in kwargs:
        ng_args = [ng_arg.strip() for ng_arg in kwargs.pop('ng_args').split(',')]
    else:
        ng_args = None

    url = reverse(name, args=args)

    # replace escaped angular tags
    if ng_args:
        for ng_arg in ng_args:
            url = url.replace(ng_arg, '{$ ' + ng_arg + ' $}')

    if text is None:
        text = url

    # add an attribute for every kwarg
    attributes = []
    for key in kwargs:
        attributes.append("%s=\"%s\"" % (key, kwargs[key]))

    return "<a href=\"%s\" %s>%s</a>" % (url, ' '.join(attributes), text)
