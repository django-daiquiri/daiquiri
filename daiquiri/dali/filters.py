import iso8601

from rest_framework.filters import BaseFilterBackend

from daiquiri.jobs.models import Job


class UWSFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):

        # apply only for list
        if view.action == 'list':
            phases = request.GET.getlist('PHASE')

            if phases:
                queryset = queryset.filter(phase__in=phases)
            else:
                queryset = queryset.exclude(phase__exact=Job.PHASE_ARCHIVED)

            after = request.GET.get('AFTER')
            if after:
                queryset = queryset.filter(start_time__gt=iso8601.parse_date(after))

            last = request.GET.get('LAST')
            if last:
                queryset = queryset.filter(start_time__isnull=False) \
                    .order_by('-start_time')[:int(last)]

        return queryset
