from __future__ import unicode_literals

import ipaddress
import importlib
import re

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.six.moves.urllib.parse import urlparse

from ipware.ip import get_real_ip


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)


def get_script_alias(request):
    return request.path[:-len(request.path_info)]


def get_referer(request, default=None):
    return request.META.get('HTTP_REFERER', default)


def get_client_ip(request):
    ip = get_real_ip(request)

    if ip:
        try:
            interface = ipaddress.IPv6Interface('%s/%i' % (ip, settings.IPV6_PRIVACY_MASK))
        except ipaddress.AddressValueError:
            interface = ipaddress.IPv4Interface('%s/%i' % (ip, settings.IPV4_PRIVACY_MASK))

        return str(interface.network.network_address)
    else:
        return None


def get_referer_path_info(request, default=None):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        return default

    script_alias = get_script_alias(request)
    return urlparse(referer).path[len(script_alias):]


def get_next(request):
    next = request.POST.get('next')
    current = request.path_info

    if next in (current, None):
        return get_script_alias(request) + '/'
    else:
        return get_script_alias(request) + next


def get_model_field_meta(model):
    meta = {}

    for field in model._meta.get_fields():
        meta[field.name] = {}
        if hasattr(field, 'verbose_name'):
            meta[field.name]['verbose_name'] = field.verbose_name
        if hasattr(field, 'help_text'):
            meta[field.name]['help_text'] = field.help_text

    return meta


def human2bytes(string):
    if not string:
        return 0

    m = re.match('([0-9.]+)\s*([A-Za-z]+)', string)
    number, unit = float(m.group(1)), m.group(2).strip().lower()

    if unit == 'kb' or unit == 'k':
        return number * 1000
    elif unit == 'mb' or unit == 'm':
        return number * 1000**2
    elif unit == 'gb' or unit == 'g':
        return number * 1000**3
    elif unit == 'tb' or unit == 't':
        return number * 1000**4
    elif unit == 'pb' or unit == 'p':
        return number * 1000**5
    elif unit == 'kib':
        return number * 1024
    elif unit == 'mib':
        return number * 1024**2
    elif unit == 'gib':
        return number * 1024**3
    elif unit == 'tib':
        return number * 1024**4
    elif unit == 'pib':
        return number * 1024**5


def send_mail(request, template_prefix, context, to_emails, cc_emails=[], bcc_emails=[]):
    '''
    This is heavily inspired by allauth.account.adapter.
    https://github.com/pennersr/django-allauth/blob/master/allauth/account/adapter.py
    '''
    # get current site
    site = get_current_site(request)

    # add site to context
    context['current_site'] = site

    # render subject from template and remove superfluous line breaks
    subject = render_to_string('{0}_subject.txt'.format(template_prefix), context)
    subject = " ".join(subject.splitlines()).strip()

    # add site name to subject
    site = get_current_site(request)
    subject = "[%s] %s" % (site.name, subject)

    # get from email
    from_email = settings.DEFAULT_FROM_EMAIL

    # render bodie(s)
    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}_message.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           context).strip()
        except TemplateDoesNotExist:
            if ext == 'txt' and not bodies:
                # We need at least one body
                raise
    if 'txt' in bodies:
        msg = EmailMultiAlternatives(subject, bodies['txt'], from_email, to_emails, cc=cc_emails, bcc=bcc_emails)
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(subject, bodies['html'], from_email, to_emails, cc=cc_emails, bcc=bcc_emails)
        msg.content_subtype = 'html'  # Main content is now text/html

    msg.send()
