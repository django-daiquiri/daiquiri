from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username of the user to promote.')
        parser.add_argument('--demote', action='store_true', default=False, help='Demote instead of promote.')

    def handle(self, *args, **options):
        is_admin = False if options['demote'] else True

        user = User.objects.get(username=options['username'])
        user.is_superuser = is_admin
        user.is_staff = is_admin
        user.save()
