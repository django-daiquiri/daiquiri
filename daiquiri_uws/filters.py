from rest_framework.filters import BaseFilterBackend

import iso8601


class UWSFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):

        # apply only for list
        if view.kwargs.get('pk') is None:
            phases = request.GET.getlist('PHASE')
            if phases:
                queryset = queryset.filter(phase__in=phases)

            after = request.GET.get('AFTER')
            if after:
                queryset = queryset.filter(start_time__gt=iso8601.parse_date(after))

            last = request.GET.get('LAST')
            if last:
                queryset = queryset.filter(start_time__isnull=False).order_by('-start_time')[:last]

        return queryset
