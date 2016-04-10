from django.shortcuts import render

from rest_framework import viewsets, mixins, filters

from .models import QueryJob
from .serializers import QueryJobSerializer


def query(request):
    return render(request, 'query/query.html', {})


class QueryJobViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = QueryJob.objects.all()
    serializer_class = QueryJobSerializer
