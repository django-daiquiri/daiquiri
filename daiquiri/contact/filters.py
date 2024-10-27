from django.core.exceptions import ValidationError

from rest_framework import filters

from daiquiri.auth.validators import DaiquiriUsernameValidator


class SpamBackend(filters.BaseFilterBackend):


    def filter_queryset(self, request, queryset, view):

        from daiquiri.contact.models import ContactMessage

        spam = request.GET.get('spam')

        if spam is not None:
            if spam == 'true':
                queryset = queryset.filter(status=ContactMessage.STATUS_SPAM)
            else:
                queryset = queryset.exclude(status=ContactMessage.STATUS_SPAM)

        return queryset



class DefaultMessageFilter:

    CHOICES = (
        ("no_filter", "Show to all users"),
        ("logged_in_users", "Show to the logged in users only"),
        ("user_has_not_consented", "Show to user who has not consented yet"),
        ("user_has_invalid_username", "Show to user with an invalid username"),
    )

    def no_filter(request):
        return True

    def logged_in_users(request):
        if request.user.is_authenticated:
            return True
        return False

    def user_has_not_consented(request):
        if request.user.is_authenticated:
            if not request.user.profile.consent:
                return True
        return False

    def user_has_invalid_username(request):
        if request.user.is_authenticated:
            try:
                DaiquiriUsernameValidator()(request.user.username)
            except ValidationError:
                return True
            return False
