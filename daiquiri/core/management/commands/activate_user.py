from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username of the user to activate.')
        parser.add_argument('--deactivate', action='store_true', default=False, help='Deactivate instead of activate.')

    def handle(self, *args, **options):
        is_active = False if options['deactivate'] else True

        user = User.objects.get(username=options['username'])
        user.is_active = is_active
        user.save()
