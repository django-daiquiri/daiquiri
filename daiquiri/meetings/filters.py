from rest_framework import filters


class ParticipantFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):

        contribution_type = request.GET.getlist('contribution_type')
        status = request.GET.getlist('status')
        payment = request.GET.getlist('payment')

        if contribution_type:
            queryset = queryset.filter(contributions__contribution_type__in=contribution_type)

        if status:
            queryset = queryset.filter(status__in=status)

        if payment:
            queryset = queryset.filter(payment__in=payment)

        return queryset
