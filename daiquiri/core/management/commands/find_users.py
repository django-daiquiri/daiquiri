import csv
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from allauth.account.models import EmailAddress

from daiquiri.auth.models import Profile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--id", default=".*", help="find users by id")
        parser.add_argument("--email", default=".*", help="find users by email")
        parser.add_argument("--username", default=".*", help="find users by username")
        parser.add_argument(
            "--first_name", default=".*", help="find users by first name"
        )
        parser.add_argument("--last_name", default=".*", help="find users by last name")
        parser.add_argument(
            "--email_verified",
            default=".*",
            help="filter users by email_verified, requires argument, supports: true/false/1/0",
        )
        parser.add_argument(
            "--profile_pending",
            default=".*",
            help="filter users by profile_pending, requires argument, supports: true/false/1/0",
        )
        parser.add_argument(
            "--profile_confirmed",
            default=".*",
            help="filter users by profile_confirmed, requires argument, supports: true/false/1/0",
        )
        parser.add_argument(
            "-p",
            "--print",
            action="store_true",
            help="print found users, don't save them to csv",
        )
        parser.add_argument(
            "-o",
            "--output_file",
            default="found_users.csv",
            help="output file, default is 'found_users.csv'",
        )

    def save_csv(self, data, filename):
        if len(data) > 1:
            data_file = open(filename, "w", newline="", encoding="utf-8")
            csv_writer = csv.DictWriter(
                data_file, fieldnames=list(data[0].keys()), dialect="unix"
            )
            csv_writer.writeheader()
            for user in data:
                csv_writer.writerow(user)
            print("List written to " + filename)

    def print_file(self, filename):
        f = open(filename)
        content = f.read()
        print(content)
        f.close()

    def get_profile(self, username):
        return Profile.objects.get(user__username=username)

    def rx_match(self, regex, s):
        return bool(re.search(regex, str(s)))

    def make_bool(self, val):
        if str(val) == "1":
            return True
        if str(val).lower() == "true":
            return True
        return False

    def bools_are_equal(self, b1, b2):
        return self.make_bool(b1) == self.make_bool(b2)

    def check_match(self, user, profile, email_verified, options):
        if self.rx_match(options["id"], user.id) is False:
            return False
        if self.rx_match(options["email"], user.email) is False:
            return False
        if self.rx_match(options["username"], user.username) is False:
            return False
        if self.rx_match(options["last_name"], user.last_name) is False:
            return False
        if (
            self.bools_are_equal(options["profile_pending"], profile.is_pending)
            is False
        ):
            return False
        if (
            self.bools_are_equal(options["profile_confirmed"], profile.is_confirmed)
            is False
        ):
            return False
        if self.bools_are_equal(options["email_verified"], email_verified) is False:
            return False
        return True

    def find_users(self, options):
        found_users = []
        for _, user in enumerate(User.objects.all().order_by("date_joined")):
            profile = Profile.objects.get(user__username=user.username)
            email = EmailAddress.objects.filter(user=user.id, verified=True).first()
            email_verified = False
            if email is not None:
                email_verified = True
            m = self.check_match(user, profile, email_verified, options)
            if m is True:
                found_users.append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "date_joined": user.date_joined,
                        "unix_joined": user.date_joined.timestamp(),
                        "email": user.email,
                        "email_verified": email_verified,
                        "last_login": user.last_login,
                        "profile_pending": profile.is_pending,
                        "profile_confirmed": profile.is_confirmed,
                    }
                )
        return found_users

    def handle(self, *args, **options):
        no_total_users = User.objects.all().count()
        print("Total no of users:    %d" % (no_total_users))
        found_users = self.find_users(options)

        print(
            "Matching the filter:  %d  %.2f%%"
            % (len(found_users), (100 / no_total_users) * len(found_users))
        )

        self.save_csv(found_users, options["output_file"])
        if options["print"] is True:
            self.print_file(options["output_file"])
