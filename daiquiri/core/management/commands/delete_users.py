import csv
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from allauth.account.models import EmailAddress


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'id_list_file',
            type=str,
            help='required list of user ids to delete in plain text or CSV format, '
            + 'user ids have to be at the beginning of the line, '
            + 'supports commenting lines out: if a line does '
            + 'not start with an integer it will be skipped',
        )
        parser.add_argument(
            '-n',
            '--dry_run',
            action='store_true',
            default=False,
            help='dry run, does not delete anything but print what ' + 'would have happened',
        )

    def make_user_id_list(self, filename: str):
        user_ids = []
        try:
            with open(filename, encoding='utf-8', newline='') as filecontent:
                first_line = filecontent.readline()
                filecontent.seek(0)
                header = next(csv.reader([first_line], dialect='unix'), [])
                if 'id' in header:
                    csv_reader = csv.DictReader(filecontent, dialect='unix')
                    for dic in csv_reader:
                        user_id = dic.get('id')
                        if user_id is not None and re.fullmatch(r'[0-9]+', user_id):
                            user_ids.append({'id': user_id})
                else:
                    for line in filecontent:
                        m = re.search(r'^[0-9]+', line)
                        if m:
                            user_ids.append({'id': m.group(0)})
        except (OSError, UnicodeError, csv.Error) as e:
            raise CommandError('Error reading id list file. ' + str(e)) from e
        return sorted(user_ids, key=lambda k: k['id'])

    def delete_users(self, users: list[dict], dry_run: bool):
        errors = []
        for user in users:
            user_str = f"id={user.get('id', '?')}"
            try:
                u = User.objects.get(id=user['id'])
                emails = list(
                    EmailAddress.objects.filter(user=u).values_list('email', flat=True)
                )
                if u.email:
                    emails.insert(0, u.email)
                emails = list(dict.fromkeys(emails))
                user_str = (
                    f'{u.id}, {u.username}, {u.first_name}, {u.last_name}, '
                    f'email(s): {", ".join(emails) or "<none>"}'
                )
                if dry_run is False:
                    print(f'Delete user {user_str}')
                    u.delete()
                else:
                    print(f'Would have deleted user: {user_str}')
            except Exception as e:
                errors.append(e)
                print(f'Error deleting user {user_str}: {e}')

        if errors:
            raise CommandError(f'{len(errors)} user(s) could not be deleted.')


    def handle(self, *args, **options):
        user_ids = self.make_user_id_list(options['id_list_file'])
        if options['dry_run'] is True:
            self.delete_users(user_ids, options['dry_run'])
        else:
            print('\nYou are about to delete ' + str(len(user_ids)) + ' users.')
            val = input("Are you sure? If so please enter 'yes' to continue?    ")
            if val == 'yes':
                self.delete_users(user_ids, options['dry_run'])
            else:
                print('\nAborted.\n')
