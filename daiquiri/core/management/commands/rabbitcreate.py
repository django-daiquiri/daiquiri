from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    requires_system_checks = []
    can_import_settings = True

    def handle(self, *args, **options):

        parsed_url = urlparse(settings.CELERY_BROKER_URL)

        vhost = parsed_url.path.lstrip('/')

        print(f'rabbitmqctl add_user {parsed_url.username} {parsed_url.password}')
        print(f'rabbitmqctl add_vhost {vhost}')
        print(f'rabbitmqctl set_permissions -p {vhost} {parsed_url.username} ".*" ".*" ".*"')
        print(f'rabbitmqctl set_permissions -p {vhost} admin ".*" ".*" ".*"')
