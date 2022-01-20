from django.core.management.base import BaseCommand

from daiquiri.datalink.adapter import DatalinkAdapter
from daiquiri.datalink.models import Datalink


class Command(BaseCommand):

    def handle(self, *args, **options):

        adapter = DatalinkAdapter()

        Datalink.objects.all().delete()

        datalinks = []
        for resource_type, resource in adapter.get_list():
            links = adapter.get_links(resource_type, resource)
            for link in links:
                datalinks.append(Datalink(**link))

        Datalink.objects.bulk_create(datalinks)
