from django.core.management.base import BaseCommand

from daiquiri.datalink.adapter import DatalinkAdapter
from daiquiri.datalink.models import Datalink


class Command(BaseCommand):

    def handle(self, *args, **options):

        adapter = DatalinkAdapter()
        Datalink.objects.all().delete()

        datalinks = []
        for row in adapter.fetch_rows():
            datalinks.append(Datalink(
               ID=row[1],
               access_url=row[2] or '',
               service_def=row[3] or '',
               error_message=row[4] or '',
               description=row[5] or '',
               semantics=row[6],
               content_type=row[7] or '',
               content_length=row[8] or 0,
            ))
        Datalink.objects.bulk_create(datalinks)
