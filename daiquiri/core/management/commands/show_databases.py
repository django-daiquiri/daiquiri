import pprint

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        pprint.pprint(settings.DATABASES, indent=4)
