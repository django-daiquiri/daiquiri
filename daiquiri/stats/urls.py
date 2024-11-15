from django.urls import include, path

from rest_framework import routers

from .views import ManagementView
from .viewsets import RecordViewSet

app_name = 'stats'

router = routers. DefaultRouter()
router.register(r'records', RecordViewSet, basename='record')

urlpatterns = [
    path('api/', include(router.urls)),

    path('management/', ManagementView.as_view(), name='management'),
]
