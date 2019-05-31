from django.urls import include, path, re_path

from .views import (
    SchemaView,
    #TableView
)

app_name = 'datacite'

urlpatterns = [
    re_path(r'^(?P<schema_name>\w+)/$', SchemaView.as_view(), name='schema'),
    # re_path(r'^(?P<schema_name>\w+)/(?P<table_name>\w+)/$', TableView.as_view(), name='table'),
]
