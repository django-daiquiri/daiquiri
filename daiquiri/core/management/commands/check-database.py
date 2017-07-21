from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Database
from daiquiri.query.utils import get_user_database_name





class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def handle(self, *args, **options):

        default = settings.DATABASES.get('default')
        tap = settings.DATABASES.get('tap')
        data = settings.DATABASES.get('data')

        print('')
        print('CREATE DATABASE %(NAME)s;' % default)
        print('GRANT ALL PRIVILEGES ON %(NAME)s.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % default)
        print('')
        print('CREATE DATABASE %(NAME)s;' % tap)
        print('GRANT ALL PRIVILEGES ON %(NAME)s.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % tap)
        print('')

        data.update({'NAME': settings.QUERY['user_database_prefix'] + '%'})

        try:
            for database in Database.objects.all():
                data.update({'NAME': database.name})
                print('GRANT SELECT ON %(NAME)s.* to \'%(USER)s\'@\'%(HOST)s\' identified by \'%(PASSWORD)s\';' % data)
        except OperationalError:
            pass
