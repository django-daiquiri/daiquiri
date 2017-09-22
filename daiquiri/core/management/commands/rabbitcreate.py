from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.six.moves.urllib.parse import urlparse


class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def handle(self, *args, **options):

        parsed_url = urlparse(settings.CELERY_BROKER_URL)

        vhost = parsed_url.path.lstrip('/')

        print('rabbitmqctl add_user %s %s' % (parsed_url.username, parsed_url.password))
        print('rabbitmqctl add_vhost %s' % vhost)
        print('rabbitmqctl set_permissions -p %s %s ".*" ".*" ".*"' % (vhost, parsed_url.username))
        print('rabbitmqctl set_permissions -p %s admin ".*" ".*" ".*"' % vhost)
