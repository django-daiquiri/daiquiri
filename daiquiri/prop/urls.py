from django.urls import include, path

from rest_framework import routers

from .viewsets import ProposalViewSet

app_name = 'prop'


router = routers.DefaultRouter()

router.register(r'proposal', ProposalViewSet, basename='proposal')

urlpatterns = [
    path('api/', include(router.urls)),
]
