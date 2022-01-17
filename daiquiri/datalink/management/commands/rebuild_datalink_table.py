from django.core.management.base import BaseCommand

from daiquiri.datalink.adapter import DatalinkAdapter
from daiquiri.datalink.models import Datalink


class Command(BaseCommand):

    def handle(self, *args, **options):

        adapter = DatalinkAdapter()
        Datalink.objects.all().delete()

        datalinks = []
        for row in adapter.fetch_rows():
            datalinks.append(Datalink(**row))
        Datalink.objects.bulk_create(datalinks)
