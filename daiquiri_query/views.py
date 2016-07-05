from django.shortcuts import render
from django.http import HttpResponseRedirect

from rest_framework import viewsets, mixins, filters

from daiquiri_metadata.models import Database, Function

from .models import QueryJob
from .serializers import QueryJobSerializer, DatabaseSerializer, FunctionSerializer
from .forms import QueryJobForm


def query(request):
    form = QueryJobForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():

            QueryJob.submission.submit(form.cleaned_data['query'], request.user)

            return HttpResponseRedirect(request.path_info)

    return render(request, 'query/query.html', {
        'form': form
    })


class QueryJobViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = QueryJob.objects.all()
    serializer_class = QueryJobSerializer


class DatabaseViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = DatabaseSerializer

    def get_queryset(self):
        return Database.objects.filter(published_for__in=self.request.user.groups.all())


class FunctionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = FunctionSerializer

    def get_queryset(self):
        return Function.objects.filter(published_for__in=self.request.user.groups.all())
