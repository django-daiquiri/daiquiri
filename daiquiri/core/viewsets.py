from rest_framework import mixins, viewsets

from .serializers import ChoicesSerializer

from rest_framework.exceptions import ParseError


class ChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChoicesSerializer


class RowViewSet(viewsets.ViewSet):

    def _get_page(self):
        try:
            return int(self.request.GET.get('page', '1'))
        except ValueError:
            raise ParseError('page must be an integer')

    def _get_page_size(self):
        try:
            return int(self.request.GET.get('page_size', '30'))
        except ValueError:
            raise ParseError('page_size must be an integer')

    def _get_filters(self):
        filters = {}
        for key, value in self.request.GET.items():
            if key not in ['database', 'table', 'column', 'ordering', 'search', 'page', 'page_size']:
                filters[key] = value
        return filters

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
