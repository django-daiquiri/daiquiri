from django.conf import settings

from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):

    def has_permission(self, request, view):
        return settings.QUERY_ANONYMOUS or (request.user and request.user.is_authenticated)
