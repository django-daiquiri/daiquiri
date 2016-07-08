from django.shortcuts import render
from django.http import HttpResponseRedirect

from rest_framework import viewsets, mixins, filters

from daiquiri_metadata.models import Database, Function

from .models import QueryJob
from .serializers import QueryJobSerializer, DatabaseSerializer, FunctionSerializer


def query(request):

    #query = 'select a,b from daiquiri_.tbl, tbl2 where c = 5'
    #query = 'select adsad(1)'
    query = 'select a.vx,b.id from daiquiri_data_sim.particles as a, daiquiri_test_obs.stars as b where b.id = 5'

    QueryJob.submission.submit(query, request.user)

    return render(request, 'query/query.html', {'query': query})


class QueryJobViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = QueryJob.objects.all()
    serializer_class = QueryJobSerializer


class DatabaseViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = DatabaseSerializer

    def get_queryset(self):
        return Database.objects.filter(groups__in=self.request.user.groups.all())


class FunctionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = FunctionSerializer

    def get_queryset(self):
        return Function.objects.filter(groups__in=self.request.user.groups.all())
