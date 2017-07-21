from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError

from daiquiri.metadata.models import Database


class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def get_config(self, key):
        config = settings.DATABASES.get(key)
        if 'HOST' not in config:
            config['HOST'] = 'localhost'
        return config

    def handle(self, *args, **options):

        default = self.get_config('default')
        tap = self.get_config('tap')
        data = self.get_config('data')

        print('')
        print('CREATE DATABASE `%(NAME)s`;' % default)
        print('GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % default)
        print('')
        print('CREATE DATABASE `%(NAME)s`;' % tap)
        print('GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % tap)
        print('')

        data.update({'NAME': settings.QUERY['user_database_prefix'] + '%'})
        print('GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % data)
        print('')

        try:
            for database in Database.objects.all():
                data.update({'NAME': database.name})
                print('GRANT SELECT ON `%(NAME)s`.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % data)
            print('')
        except (OperationalError, ProgrammingError):
            pass
