from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import availability, capabilities, resource
from .viewsets import ConeSearchView

app_name = 'conesearch'

urlpatterns = [
    path('', TemplateView.as_view(template_name='conesearch/root.html'), name='root'),
    path('resource', resource, name='resource'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),
    re_path(r'^api/(?P<resource>.+)/$', ConeSearchView.as_view(), name='search'),
]
