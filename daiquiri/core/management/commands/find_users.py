import csv
import re
from io import StringIO

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from allauth.account.models import EmailAddress
from django.db.models import CharField

from daiquiri.auth.models import Profile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--id', default='.*', help='find users by id')
        parser.add_argument('--email', default='.*', help='find users by email')
        parser.add_argument('--username', default='.*', help='find users by username')
        parser.add_argument('--first_name', default='.*', help='find users by first name')
        parser.add_argument('--last_name', default='.*', help='find users by last name')
        parser.add_argument(
            '--email_verified',
            default=None,
            help='filter users by email_verified, requires argument, supports: true/false/1/0',
        )
        parser.add_argument(
            '--profile_pending',
            default=None,
            help='filter users by profile_pending, requires argument, supports: true/false/1/0',
        )
        parser.add_argument(
            '--profile_confirmed',
            default=None,
            help='filter users by profile_confirmed, requires argument, supports: true/false/1/0',
        )
        parser.add_argument(
            '-p',
            '--print',
            action='store_true',
            help="print found users, don't save them to csv",
        )
        parser.add_argument(
            '-o',
            '--output_file',
            default='found_users.csv',
            help="output file, default is 'found_users.csv'",
        )

    def save_csv(self, users: list[dict], filename: str):
        content = self._users_to_csv_string(users)
        with open(filename, 'w', newline='', encoding='utf-8') as fd:
            fd.write(content)
        print('Users written to ' + filename)

    def print_users(self, users: list[dict]):
        print(self._users_to_csv_string(users))

    def get_profile(self, username: str):
        return Profile.objects.get(user__username=username)

    def rx_match(self, regex: str, s: str | CharField):
        try:
            return bool(re.search(regex, str(s)))
        except re.error as e:
            raise CommandError(f'Invalid regular expression: "{regex}": {e}') from e

    def make_bool(self, val):
        s = str(val).lower()
        if s in ('1', 'true'):
            return True
        elif s in ('0', 'false'):
            return False
        else:
            raise CommandError(
                f'Invalid boolean value: "{val}". Allowed values are : true/false/1/0'
            )

    def option_matches_bool(self, b1, b2) -> bool:
        return self.make_bool(b1) == self.make_bool(b2)

    def check_match(
        self, user: User, profile: Profile, email_verified: bool, options: dict
    ) -> bool:
        if self.rx_match(options['id'], user.id) is False:
            return False
        if self.rx_match(options['email'], user.email) is False:
            return False
        if self.rx_match(options['username'], user.username) is False:
            return False
        if self.rx_match(options['first_name'], user.last_name) is False:
            return False
        if self.rx_match(options['last_name'], user.last_name) is False:
            return False
        if (
            options['profile_pending'] is not None
            and self.option_matches_bool(options['profile_pending'], profile.is_pending) is False
        ):
            return False
        if (
            options['profile_confirmed'] is not None
            and self.option_matches_bool(options['profile_confirmed'], profile.is_confirmed)
            is False
        ):
            return False
        if (
            options['email_verified'] is not None
            and self.option_matches_bool(options['email_verified'], email_verified) is False
        ):
            return False
        return True

    def find_users(self, options: dict) -> list[dict]:
        found_users = []
        for _, user in enumerate(User.objects.all().order_by('date_joined')):
            profile = Profile.objects.get(user__username=user.username)
            email = EmailAddress.objects.filter(user=user.id, verified=True).first()
            email_verified = True if email is not None else False
            m = self.check_match(user, profile, email_verified, options)
            if m is True:
                found_users.append(
                    {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'date_joined': user.date_joined,
                        'unix_joined': user.date_joined.timestamp(),
                        'email': user.email,
                        'email_verified': email_verified,
                        'last_login': user.last_login,
                        'profile_pending': profile.is_pending,
                        'profile_confirmed': profile.is_confirmed,
                    }
                )
        return found_users

    def handle(self, *args, **options):
        num_total_users = User.objects.all().count()
        found_users = self.find_users(options)
        found_users_percent = (
            (100.0 / num_total_users) * len(found_users) if num_total_users > 0 else 0
        )

        print(f'Total number of users:    {num_total_users}')
        print(f'Matching the filter:  {len(found_users)}  {found_users_percent:.2f}%')

        if options['print'] is True:
            self.print_users(found_users)
        else:
            self.save_csv(found_users, options['output_file'])

    def _users_to_csv_string(self, users: list[dict]) -> str:
        output = StringIO()
        fieldnames = list(users[0].keys()) if len(users) > 0 else []
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames, dialect='unix')
        if fieldnames:
            csv_writer.writeheader()
        for user in users:
            csv_writer.writerow(user)
        return output.getvalue()
