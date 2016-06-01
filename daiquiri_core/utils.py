from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
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


def get_next_redirect(request):
    next = request.POST.get('next')
    current_url_name = resolve(request.path_info).url_name

    if next in (current_url_name, None):
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse(next))


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
