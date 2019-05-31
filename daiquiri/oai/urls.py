from django.urls import path

from .views import OAIPMHView


app_name = 'oai'

urlpatterns = [
    path('', OAIPMHView.as_view(), name='oai-pmh'),
]
