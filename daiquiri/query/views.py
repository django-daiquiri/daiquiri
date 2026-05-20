from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from daiquiri.core.utils import get_model_field_meta
from daiquiri.core.views import (
    AnonymousAccessMixin,
    CSRFViewMixin,
    ModelPermissionMixin,
    StoreIdViewMixin,
)

from .models import Example, QueryJob


class QueryView(AnonymousAccessMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):
    template_name = 'query/query.html'
    anonymous_setting = 'QUERY_ANONYMOUS'

