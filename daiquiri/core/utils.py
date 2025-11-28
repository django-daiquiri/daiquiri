import csv
import importlib
import ipaddress
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse
from xml.dom import minidom

from django import forms
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import date
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

import xlsxwriter
from ipware import get_client_ip as ipware_get_client_ip
from markdown import markdown as markdown_function

from daiquiri.core.constants import (
    ACCESS_LEVEL_INTERNAL,
    ACCESS_LEVEL_PRIVATE,
    ACCESS_LEVEL_PUBLIC,
    GROUPS,
)

if sys.version_info.major >= 3:
    long_type = int
else:
    long_type = long  # noqa: F821


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)


def get_script_alias(request):
    return request.path[: -len(request.path_info)]


def get_referer(request, default=None):
    return request.META.get('HTTP_REFERER', default)


def get_client_ip(request):
    client_ip, is_routable = ipware_get_client_ip(request)

    if client_ip:
        try:
            interface = ipaddress.IPv6Interface(f'{client_ip}/{int(settings.IPV6_PRIVACY_MASK)}')
        except ipaddress.AddressValueError:
            interface = ipaddress.IPv4Interface(f'{client_ip}/{int(settings.IPV4_PRIVACY_MASK)}')

        return str(interface.network.network_address)
    else:
        return None


def get_referer_path_info(request, default=None):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        return default

    script_alias = get_script_alias(request)
    return urlparse(referer).path[len(script_alias) :]


def get_next(request):
    next = request.POST.get('next')
    current = request.path_info

    if next in (current, None):
        return get_script_alias(request) + '/'
    else:
        return get_script_alias(request) + next


def get_model_field_meta(*models):
    meta = defaultdict(lambda: defaultdict(dict))

    for model in models:
        for field in model._meta.get_fields():
            if hasattr(field, 'verbose_name'):
                meta[model._meta.model_name][field.name]['verbose_name'] = field.verbose_name
            if hasattr(field, 'help_text'):
                meta[model._meta.model_name][field.name]['help_text'] = field.help_text

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
            field = forms.CharField(
                widget=forms.TextInput(attrs={'placeholder': detail_key['label']})
            )
        elif detail_key['data_type'] == 'textarea':
            field = forms.CharField(
                widget=forms.Textarea(attrs={'placeholder': detail_key['label']})
            )
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


def get_permission_emails(permissions):
    permissions_queryset = Permission.objects
    for permission in permissions:
        app_label, codename = permission.split('.')
        permissions_queryset = permissions_queryset.filter(
            content_type__app_label=app_label, codename=codename
        )

    users = User.objects.filter(
        Q(groups__permissions__in=permissions_queryset)
        | Q(user_permissions__in=permissions_queryset)
    ).distinct()

    return [user.email for user in users]


def get_doi_url(doi):
    return 'https://doi.org/{}'.format(doi.rstrip('/')) if doi else None


def get_doi(doi_url):
    return urlparse(doi_url).path.lstrip('/') if doi_url else None


def filter_by_access_level(user, items):
    filtered_items = []

    for item in items:
        # check for the access level of the queue
        if 'access_level' not in item or item['access_level'] == ACCESS_LEVEL_PUBLIC:
            filtered_items.append(item)
        elif item['access_level'] == ACCESS_LEVEL_INTERNAL:
            if user is not None:
                if user.is_authenticated:
                    filtered_items.append(item)
        elif item['access_level'] == ACCESS_LEVEL_PRIVATE and 'groups' in item:
            if user is not None:
                if user.is_authenticated and user.groups.filter(name__in=item['groups']).exists():
                    filtered_items.append(item)

    return filtered_items


def human2bytes(string):
    if not string:
        return 0

    m = re.match(r'([0-9.]+)\s*([A-Za-z]+)', string)
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


def bytes2human(size, gnu=True):
    if gnu:
        for unit in ['B', 'kB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1000.0 or unit == 'PB':
                return f'{size:.1f} {unit}'
            size /= 1000.0
    else:
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
            if size < 1024.0 or unit == 'PiB':
                return f'{size:.1f} {unit}'
            size /= 1024.0


def markdown(md):
    return markdown_function(
        md,
        extensions=['fenced_code', 'attr_list', 'codehilite'],
        extension_configs={'codehilite': {'guess_lang': 'false'}},
    )


def make_query_dict_upper_case(input_dict):
    output_dict = input_dict.copy()

    for key in input_dict.keys():
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
        try:
            permission = Permission.objects.get(
                content_type__app_label=app_label, codename=codename
            )
            group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass

    return group, created


def send_mail(request, template_prefix, context, to_emails, cc_emails=[], bcc_emails=[]):
    """
    This is heavily inspired by allauth.account.adapter.
    https://github.com/pennersr/django-allauth/blob/master/allauth/account/adapter.py
    """
    # get current site
    site = get_current_site(request)

    # add site to context
    context['current_site'] = site

    # render subject from template and remove superfluous line breaks
    subject = render_to_string(f'{template_prefix}_subject.txt', context)
    subject = ' '.join(subject.splitlines()).strip()

    # add site name to subject
    site = get_current_site(request)
    subject = f'[{site.name}] {subject}'

    # get from email
    from_email = settings.DEFAULT_FROM_EMAIL

    # get reply_to
    reply_to = settings.EMAIL_REPLY_TO

    # render bodie(s)
    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = f'{template_prefix}_message.{ext}'
            bodies[ext] = render_to_string(template_name, context).strip()
        except TemplateDoesNotExist:
            if ext == 'txt' and not bodies:
                # We need at least one body
                raise
    if 'txt' in bodies:
        msg = EmailMultiAlternatives(
            subject,
            bodies['txt'],
            from_email,
            to_emails,
            cc=cc_emails,
            bcc=bcc_emails,
            reply_to=reply_to,
        )
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(
            subject,
            bodies['html'],
            from_email,
            to_emails,
            cc=cc_emails,
            bcc=bcc_emails,
            reply_to=reply_to,
        )
        msg.content_subtype = 'html'  # Main content is now text/html

    msg.send()


def render_to_csv(request, filename, columns, rows):
    response = HttpResponse(content_type='text/csv', charset='utf-8')
    response['Content-Disposition'] = (f'attachment; filename="{filename}.csv"').encode()

    writer = csv.writer(response)

    writer.writerow(tuple(columns))

    for row in rows:
        writer.writerow(tuple(row))

    return response


def render_to_xlsx(request, filename, columns, rows):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        charset='utf-8',
    )
    response['Content-Disposition'] = (f'attachment; filename="{filename}.xlsx"').encode()

    workbook = xlsxwriter.Workbook(response, {'in_memory': True, 'strings_to_formulas': False})
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
                worksheet.write(i + 1, j, localtime(cell).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                try:
                    worksheet.write(i + 1, j, unicode(cell))
                except NameError:
                    worksheet.write(i + 1, j, str(cell))

    workbook.close()

    return response


def render_to_xml(request, renderer, data, filename=None, content_type='application/xml'):
    # crete xml structure
    xml = renderer.render(data)

    # prettify xml
    pretty_xml = minidom.parseString(xml).toprettyxml()

    response = HttpResponse(pretty_xml, content_type=content_type)
    if filename:
        response['Content-Disposition'] = f'filename="{filename}"'
    return response


def handle_file_upload(directory, file):
    file_path = os.path.join(directory, file.name)

    os.makedirs(directory, exist_ok=True)

    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return file_path


def sanitize_str(strval):
    return re.sub(r'[^a-zA-Z0-9]', '_', strval.lower())


def get_file_size(file_path):
    try:
        return os.stat(file_path).st_size
    except (FileNotFoundError, TypeError):
        return 0


def get_date_display(value):
    return date(value, settings.DATETIME_FORMAT)

