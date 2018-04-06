from django.conf import settings
from django.http import FileResponse

from rest_framework.exceptions import NotFound, ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.adapter.stream import BaseServiceAdapter
from daiquiri.core.utils import import_class
from daiquiri.core.generators import generate_votable


def ConeSearchAdapter():
    return import_class(settings.CONESEARCH_ADAPTER)()


class BaseConeSearchAdapter(BaseServiceAdapter):

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

    defaults = {}

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

    def stream(self):
        return FileResponse(generate_votable(DatabaseAdapter().fetchall(self.sql, self.args), self.columns), content_type='application/xml')


class SimpleConeSearchAdapter(BaseConeSearchAdapter):

    def clean(self, request, resource):
        if resource != settings.CONESEARCH_TABLE:
            raise NotFound()

        adapter = DatabaseAdapter()

        self.sql = '''
SELECT %(id_field)s, %(ra_field)s, %(dec_field)s
FROM %(schema)s.%(table)s
WHERE
    %(ra_field)s BETWEEN (%%(RA)s - 0.5 * %%(SR)s) AND (%%(RA)s + 0.5 * %%(SR)s)
AND
    %(dec_field)s BETWEEN (%%(DEC)s - 0.5 * %%(SR)s) AND (%%(DEC)s + 0.5 * %%(SR)s)
''' % {
            'id_field': adapter.escape_identifier('id'),
            'ra_field': adapter.escape_identifier('ra'),
            'dec_field': adapter.escape_identifier('dec'),
            'schema': settings.CONESEARCH_SCHEMA,
            'table': settings.CONESEARCH_TABLE
        }

        self.args, errors = self.parse_query_dict(request)

        if errors:
            raise ValidationError(errors)
