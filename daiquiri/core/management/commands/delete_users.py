import csv
import re
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "id_list_file",
            type=str,
            help="required list of user ids to delete in plain text format, "
            + "user ids have to be at the beginning of the line, "
            + "supports commenting lines out: if a line does "
            + "not start with an integer it will be skipped",
        )
        parser.add_argument(
            "-n",
            "--dry_run",
            action="store_true",
            default=False,
            help="dry run, does not delete anything but print what "
            + "would have happened",
        )

    def make_user_id_list(self, filename):
        user_ids = []
        try:
            filecontent = open(filename, encoding="utf-8", newline="")
        except Exception as e:
            print("Error reading id list file. " + str(e))
            sys.exit(1)
        else:
            csv_reader = csv.DictReader(filecontent, dialect="unix")
            for dic in csv_reader:
                m = re.search(r"^[0-9]+$", dic["id"])
                if bool(m) is True:
                    user_ids.append(dic)
        return sorted(user_ids, key=lambda k: k["id"])

    def delete_users(self, user_dic, dry_run):
        for dic in user_dic:
            try:
                u = User.objects.get(id=dic["id"])
                if dry_run is False:
                    print("Delete user {}, {}".format(dic["id"], dic["email"]))
                    u.delete()
                else:
                    print("Would have deleted user: {}, {}".format(dic["id"], dic["email"]))
            except Exception as e:
                print("Error deleting user " + str(id) + ". " + str(e))

    def handle(self, *args, **options):
        user_ids = self.make_user_id_list(options["id_list_file"])
        if options["dry_run"] is True:
            self.delete_users(user_ids, options["dry_run"])
        else:
            print("\nYou are about to delete " + str(len(user_ids)) + " users.")
            val = input("Are you sure? If so please enter 'yes' to continue?    ")
            if val == "yes":
                self.delete_users(user_ids, options["dry_run"])
            else:
                print("\nAborted.\n")
