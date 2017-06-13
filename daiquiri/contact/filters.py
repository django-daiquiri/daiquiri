from rest_framework import filters

from .models import ContactMessage


class SpamBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        spam = request.GET.get('spam')

        if spam is not None:
            if spam == 'true':
                queryset = queryset.filter(status=ContactMessage.STATUS_SPAM)
            else:
                queryset = queryset.exclude(status=ContactMessage.STATUS_SPAM)

        return queryset
