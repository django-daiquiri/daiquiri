from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from daiquiri.metadata.models import Column, Schema, Table
from daiquiri.tap.constants import TAP_SCHEMA_METADATA


class Command(BaseCommand):

    def handle(self, *args, **options):
        # remove the current tap schema
        try:
            Schema.objects.get(name=settings.TAP_SCHEMA).delete()
        except Schema.DoesNotExist:
            pass

        schema = Schema()
        schema.name = settings.TAP_SCHEMA
        schema.description = TAP_SCHEMA_METADATA['description']
        schema.order = TAP_SCHEMA_METADATA['order']
        schema.access_level = TAP_SCHEMA_METADATA['access_level']
        schema.metadata_access_level = TAP_SCHEMA_METADATA['metadata_access_level']
        schema.save()

        for table_metadata in TAP_SCHEMA_METADATA['tables']:
            table = Table()
            table.schema = schema
            table.name = table_metadata['name']
            table.description = table_metadata['description']
            table.order = table_metadata['order']
            table.access_level = table_metadata['access_level']
            table.metadata_access_level = table_metadata['metadata_access_level']
            table.save()

            for column_metadata in table_metadata['columns']:
                column = Column()
                column.table = table
                column.name = column_metadata['name']
                column.description = column_metadata['description']
                column.order = column_metadata['order']
                column.datatype = column_metadata['datatype']
                column.arraysize = column_metadata['arraysize']
                column.std = column_metadata['std']
                column.access_level = column_metadata['access_level']
                column.metadata_access_level = column_metadata['metadata_access_level']
                column.save()

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.constants import DATALINK_FIELDS, DATALINK_TABLE

            table = Table()
            table.schema = schema
            table.name = DATALINK_TABLE['name']
            table.description = DATALINK_TABLE['description']
            table.order = DATALINK_TABLE['order']
            table.access_level = DATALINK_TABLE['access_level']
            table.metadata_access_level = DATALINK_TABLE['metadata_access_level']
            table.save()

            for column_metadata in DATALINK_FIELDS:
                column = Column()
                column.table = table
                column.name = column_metadata['name']
                column.order = column_metadata['order']
                column.description = column_metadata['description']
                column.ucd = column_metadata['ucd']
                column.datatype = column_metadata['datatype']
                column.arraysize = column_metadata['arraysize']
                column.std = column_metadata['std']
                column.access_level = column_metadata['access_level']
                column.metadata_access_level = column_metadata['metadata_access_level']
                column.save()
