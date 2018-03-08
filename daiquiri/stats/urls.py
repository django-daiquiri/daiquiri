from django.conf.urls import url

from .views import ManagementView


urlpatterns = [
    url(r'^management/$', ManagementView.as_view(), name='management'),
]
