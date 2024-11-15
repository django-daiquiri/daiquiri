from django.urls import path

from .views import OaiView

app_name = 'oai'

urlpatterns = [
    path('', OaiView.as_view(), name='root'),
]
