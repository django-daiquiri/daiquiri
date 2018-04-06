from rest_framework import filters

from .models import QueryJob


class JobFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):

        phases = request.GET.getlist('phase')
        archived = request.GET.get('archived')

        if phases:
            queryset = queryset.filter(phase__in=phases)

        if archived is not None:
            if archived:
                queryset = queryset.filter(phase=QueryJob.PHASE_ARCHIVED)
            else:
                queryset = queryset.exclude(phase=QueryJob.PHASE_ARCHIVED)

        return queryset
