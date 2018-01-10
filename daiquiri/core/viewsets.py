from django.utils.translation import ugettext_lazy as _

from rest_framework import mixins, viewsets

from .serializers import ChoicesSerializer

from rest_framework.exceptions import ParseError


class ChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChoicesSerializer


class RowViewSetMixin(object):

    def _get_query_params(self, column_names):
        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        search = self.request.GET.get('search')

        # get the page from the querystring and make sure it is an int
        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            raise ParseError(_('page must be an integer'))

        # get the page_size from the querystring and make sure it is an int
        try:
            page_size = int(self.request.GET.get('page_size', '30'))
        except ValueError:
            raise ParseError(_('page_size must be an integer'))

        # get additional filters from the querystring
        filters = {}
        for key, value in self.request.GET.items():
            if key in column_names:
                filters[key] = value

        return ordering, page, page_size, search, filters

    def _get_next_url(self, page, page_size, count):
        if page * page_size < count:
            querydict = self.request.GET.copy()
            querydict['page'] = page + 1
            return self.request.build_absolute_uri(self.request.path_info + '?' + querydict.urlencode())
        else:
            return None

    def _get_previous_url(self, page):
        if page > 1:
            querydict = self.request.GET.copy()
            querydict['page'] = page - 1
            return self.request.build_absolute_uri(self.request.path_info + '?' + querydict.urlencode())
        else:
            return None
