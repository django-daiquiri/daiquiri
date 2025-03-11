from rest_framework.permissions import BasePermission


class IsAuthManager(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.has_perms([
            'daiquiri_auth.view_profile',
            'daiquiri_auth.change_profile'
        ])


class GroupViewPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.has_perms([
            'auth.view_group',
        ])
