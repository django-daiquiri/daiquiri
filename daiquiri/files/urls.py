from django.urls import re_path

from .views import FileView, SearchView

app_name = 'files'

urlpatterns = [
    re_path(r'^search/', SearchView.as_view(), name='search'),
    re_path(r'^(?P<file_path>.*)$', FileView.as_view(), name='file'),
]
