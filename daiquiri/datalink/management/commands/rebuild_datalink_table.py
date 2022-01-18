from django.core.management.base import BaseCommand

from daiquiri.datalink.adapter import DatalinkAdapter
from daiquiri.datalink.models import Datalink
from daiquiri.datalink.utils import update_links


class Command(BaseCommand):

    def handle(self, *args, **options):

        adapter = DatalinkAdapter()

        Datalink.objects.all().delete()

        for resource_type, resource in adapter.get_list():
            update_links(resource_type, resource)
