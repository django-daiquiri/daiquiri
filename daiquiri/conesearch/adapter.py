from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import import_class, make_query_dict_upper_case


def ConeSearchAdapter():
    return import_class(settings.CONESEARCH_ADAPTER)()


class BaseAdapter(object):

    def clean():
        raise NotImplementedError()

    def fetch_columns():
        raise NotImplementedError()

    def fetch_rows():
        raise NotImplementedError()


class DefaultAdapter(BaseAdapter):

    keys = ['RA', 'DEC', 'SR']

    ranges = {
        'RA': {
            'min': 0,
            'max': 360
        },
        'DEC': {
            'min': -90,
            'max': 90
        },
        'SR': {
            'min': 0,
            'max': 10
        }
    }

    columns = [
        {
            'name': 'id',
            'ucd': 'meta.id; meta.main',
            'datatype': 'char',
            'arraysize': '*'
        },
        {
            'name': 'RA',
            'ucd': 'pos.eq.ra; meta.main',
            'datatype': 'double'
        },
        {
            'name': 'DEC',
            'ucd': 'pos.eq.dec; meta.main',
            'datatype': 'double'
        }
    ]

    def clean(self, request):
        data = make_query_dict_upper_case(request.GET)

        self.sql = settings.CONESEARCH_STMT
        self.args = {}

        errors = {}
        for key in self.keys:
            try:
                value = float(data[key])

                if self.ranges[key]['min'] <= value <= self.ranges[key]['max']:
                    self.args[key] = value
                else:
                    errors[key] = [_('This value must be between %(min)g and %(max)g.' % self.ranges[key])]

            except KeyError:
                errors[key] = [_('This field may not be blank.')]

        if errors:
            raise ValidationError(errors)

    def fetch_columns(self):
        return self.columns

    def fetch_rows(self):
        return DatabaseAdapter().fetchall(self.sql, self.args)
