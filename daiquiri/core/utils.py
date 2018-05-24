from __future__ import unicode_literals

import unicodecsv as csv
import ipaddress
import importlib
import math
import re
import sys

from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from ipware.ip import get_real_ip

import xlsxwriter

if sys.version_info.major >= 3:
    long_type = int
else:
    long_type = long

from daiquiri.core.constants import (
    GROUPS,
    ACCESS_LEVEL_PRIVATE,
    ACCESS_LEVEL_INTERNAL,
    ACCESS_LEVEL_PUBLIC
)


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


def get_detail_fields(detail_keys):
    fields = []

    # add a field for each detail key
    for detail_key in detail_keys:

        if 'options' in detail_key:
            choices = [(option['id'], option['label']) for option in detail_key['options']]
        else:
            choices = []

        if detail_key['data_type'] == 'text':
            field = forms.CharField(widget=forms.TextInput(attrs={'placeholder': detail_key['label']}))
        elif detail_key['data_type'] == 'textarea':
            field = forms.CharField(widget=forms.Textarea(attrs={'placeholder': detail_key['label']}))
        elif detail_key['data_type'] == 'select':
            field = forms.ChoiceField(choices=choices)
        elif detail_key['data_type'] == 'radio':
            field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect)
        elif detail_key['data_type'] == 'multiselect':
            field = forms.MultipleChoiceField(choices=choices)
        elif detail_key['data_type'] == 'checkbox':
            field = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
        else:
            raise Exception('Unknown detail key data type.')

        if 'label' in detail_key:
            field.label = detail_key['label']

        if 'required' in detail_key:
            field.required = detail_key['required']

        if 'help_text' in detail_key:
            field.help_text = detail_key['help_text']

        fields.append((detail_key['key'], field))

    return fields


def get_admin_emails():
    return [user.email for user in User.objects.filter(is_superuser=True)]


def get_doi_url(doi):
    return 'https://doi.org/%s' % doi.rstrip('/') if doi else None


def filter_by_access_level(user, items):
    filtered_items = []

    for item in items:
        # check for the access level of the queue
        if 'access_level' not in item or item['access_level'] == ACCESS_LEVEL_PUBLIC:
            filtered_items.append(item)
        elif item['access_level'] == ACCESS_LEVEL_INTERNAL:
            if user is not None:
                filtered_items.append(item)
        elif item['access_level'] == ACCESS_LEVEL_PRIVATE and 'groups' in item:
            if user is not None and user.groups.filter(name__in=item['groups']).exists():
                filtered_items.append(item)

    return filtered_items


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


def make_query_dict_upper_case(input_dict):
    output_dict = input_dict.copy()

    for key in output_dict.keys():
        if key.upper() != key:
            values = output_dict.getlist(key)

            if key.upper() in output_dict:
                output_dict.appendlist(key.upper(), values)
            else:
                output_dict.setlist(key.upper(), values)

            output_dict.pop(key)

    return output_dict


def fix_for_json(elements):
    # first convert to a list
    elements_list = list(elements)

    # then, fix stuff or run the function recursively
    for i in range(len(elements_list)):
        # for a list run fix_for_json recursively
        if isinstance(elements_list[i], (list, tuple)):
            elements_list[i] = fix_for_json(elements_list[i])

        # check the float fields for nan
        elif isinstance(elements_list[i], float) and math.isnan(elements_list[i]):
            elements_list[i] = None

        # convert a long fields to a strings
        elif isinstance(elements_list[i], long_type) and elements_list[i] > 9007199254740991:
            elements_list[i] = str(elements_list[i])

    return elements_list


def setup_group(name):
    group, created = Group.objects.get_or_create(name=name)
    group.permissions.clear()

    for row in GROUPS[name]:
        app_label, codename = row.split('.')
        group.permissions.add(Permission.objects.get(content_type__app_label=app_label, codename=codename))

    return group, created


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

    # get reply_to
    reply_to = settings.EMAIL_REPLY_TO

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
        msg = EmailMultiAlternatives(subject, bodies['txt'], from_email, to_emails, cc=cc_emails, bcc=bcc_emails, reply_to=reply_to)
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(subject, bodies['html'], from_email, to_emails, cc=cc_emails, bcc=bcc_emails, reply_to=reply_to)
        msg.content_subtype = 'html'  # Main content is now text/html

    msg.send()


def render_to_csv(request, filename, columns, rows):
    response = HttpResponse(content_type='text/csv', charset='utf-8')
    response['Content-Disposition'] = ('attachment; filename="%s.csv"' % filename).encode('utf-8')

    writer = csv.writer(response)

    writer.writerow(tuple(columns))

    for row in rows:
        writer.writerow(tuple(row))

    return response


def render_to_xlsx(request, filename, columns, rows):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', charset='utf-8')
    response['Content-Disposition'] = ('attachment; filename="%s.xlsx"' % filename).encode('utf-8')

    workbook = xlsxwriter.Workbook(response, {
        'in_memory': True,
        'strings_to_formulas': False
    })
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    for j, column in enumerate(columns):
        worksheet.write(0, j, str(column), bold)

    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            if isinstance(cell, list):
                worksheet.write(i + 1, j, ', '.join(cell))
            elif isinstance(cell, bool):
                worksheet.write(i + 1, j, str(_('yes') if cell else _('no')))
            elif isinstance(cell, datetime):
                worksheet.write(i + 1, j, localtime(cell).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                worksheet.write(i + 1, j, cell)

    workbook.close()

    return response
