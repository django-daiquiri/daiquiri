from django.db import models


class PermissionsManager(models.Manager):

    def check_group(self, name, group):
        results = self.get_queryset().filter(name=name).filter(group=group)
        if results:
            return True
        else:
            return False

    def check_user(self, name, user):
        results = self.get_queryset().filter(name=name).filter(groups__in=user.groups.all())
        if results:
            return True
        else:
            return False
