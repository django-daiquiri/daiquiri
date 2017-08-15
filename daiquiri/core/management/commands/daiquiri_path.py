import imp

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(imp.find_module('daiquiri')[1])
