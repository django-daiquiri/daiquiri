import imp

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    requires_system_checks = []
    can_import_settings = False

    def handle(self, *args, **options):
        print(imp.find_module('daiquiri')[1])
