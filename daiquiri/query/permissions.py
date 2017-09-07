from django.conf import settings

from rest_framework.permissions import BasePermission
from rest_framework.compat import is_authenticated


class HasPermission(BasePermission):

    def has_permission(self, request, view):
        return settings.QUERY_ANONYMOUS or (request.user and is_authenticated(request.user))
