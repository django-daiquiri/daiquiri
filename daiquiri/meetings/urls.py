from django.conf.urls import url, include

from rest_framework import routers

from .views import registration, registration_done, participants, contributions, ManagementView
from .viewsets import MeetingViewSet, ParticipantViewSet, ContributionViewSet, ContributionTypeViewSet

router = routers.DefaultRouter()
router.register(r'meetings', MeetingViewSet, base_name='meeting')
router.register(r'participants', ParticipantViewSet, base_name='participant')
router.register(r'contributions', ContributionViewSet, base_name='contribution')
router.register(r'contributiontypes', ContributionTypeViewSet, base_name='contributiontype')

urlpatterns = [
    url(r'^api/', include(router.urls)),

    url(r'^(?P<slug>[-\w]+)/registration/$', registration, name='registration'),
    url(r'^(?P<slug>[-\w]+)/registration/done/$', registration_done, name='registration_done'),
    url(r'^(?P<slug>[-\w]+)/participants/$', participants, name='participants'),
    url(r'^(?P<slug>[-\w]+)/contributions/$', contributions, name='contributions'),
    url(r'^(?P<slug>[-\w]+)/management/$', ManagementView.as_view(), name='management'),
]
