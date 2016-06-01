from django.shortcuts import render
from django.http import HttpResponseRedirect

from rest_framework import viewsets, mixins, filters

from .models import QueryJob
from .serializers import QueryJobSerializer
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
