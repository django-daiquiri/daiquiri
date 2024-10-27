from rest_framework.filters import BaseFilterBackend

import iso8601

from daiquiri.core.utils import make_query_dict_upper_case
from daiquiri.jobs.models import Job


class UWSFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        query_dict = make_query_dict_upper_case(request.GET)

        # apply only for list
        if view.action == 'list':
            phases = query_dict.getlist('PHASE')

            if phases:
                queryset = queryset.filter(phase__in=phases)
            else:
                queryset = queryset.exclude(phase__exact=Job.PHASE_ARCHIVED)

            after = query_dict.get('AFTER')
            if after:
                queryset = queryset.filter(creation_time__gt=iso8601.parse_date(after))

            last = query_dict.get('LAST')
            if last:
                queryset = queryset.filter(start_time__isnull=False) \
                    .order_by('-start_time')[:int(last)]

        return queryset
