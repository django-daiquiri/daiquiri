from django.conf.urls import url

from .views import FileView


urlpatterns = [
    url(r'^(?P<file_path>.*)$', FileView.as_view(), name='file'),
]
