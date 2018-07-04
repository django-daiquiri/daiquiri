from rest_framework import filters


class ParticipantFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):

        status = request.GET.getlist('status')
        payment = request.GET.getlist('payment')

        if status:
            queryset = queryset.filter(status__in=status)

        if payment:
            queryset = queryset.filter(payment__in=payment)

        return queryset
