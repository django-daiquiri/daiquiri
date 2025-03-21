from django.conf import settings
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin

from .models import Record


class ManagementView(ModelPermissionMixin, TemplateView):
    template_name = 'stats/management.html'
    permission_required = 'daiquiri_stats.view_record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['resource_types'] = settings.STATS_RESOURCE_TYPES

        for resource_type in context['resource_types']:
            queryset = Record.objects.filter(resource_type=resource_type['key'])

            resource_type['count'] = queryset.count()
            resource_type['client_ips'] = queryset.order_by('client_ip').values('client_ip').distinct().count()
            resource_type['users'] = queryset.order_by('user').values('user').distinct().count()
            resource_type['size'] = sum(queryset.filter(size__gte=0).values_list('size', flat=True))

        return context
