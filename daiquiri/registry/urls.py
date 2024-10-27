from django.urls import path
from django.views.generic import TemplateView

from .views import authority, availability, capabilities, resource, web

app_name = 'registry'


urlpatterns = [
    path('', TemplateView.as_view(template_name='registry/root.html'), name='root'),
    path('resource', resource, name='resource'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),
    path('authority/resource', authority, name='authority'),
    path('web/resource', web, name='web'),
]
