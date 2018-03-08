from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import import_class, make_query_dict_upper_case


def ConeSearchAdapter():
    return import_class(settings.CONESEARCH_ADAPTER)()


class DefaultAdapter(object):

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

    def clean(self, request):
        data = make_query_dict_upper_case(request.GET)

        self.sql = settings.CONESEARCH_STMT
        self.sql_args = {}

        errors = {}
        for key in self.keys:
            try:
                value = float(data[key])
            except KeyError:
                errors[key] = [_('This field may not be blank.')]

            if self.ranges[key]['min'] <= value <= self.ranges[key]['max']:
                self.sql_args[key] = value
            else:
                errors[key] = [_('This value must be between %(min)g and %(max)g.' % self.ranges[key])]

        if errors:
            raise ValidationError(errors)

    def fetch_rows(self):
        return DatabaseAdapter().fetchall(self.sql, self.sql_args)
