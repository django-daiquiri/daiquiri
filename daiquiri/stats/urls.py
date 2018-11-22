from django.urls import path

from .views import ManagementView


app_name = 'stats'

urlpatterns = [
    path('management/', ManagementView.as_view(), name='management'),
]
