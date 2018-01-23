from django.conf.urls import url, include

from rest_framework import routers

from .views import registration, registration_done, participants, contributions
#from .viewsets import MeetingViewSet, ParticipantViewSet, ContributionViewSet

router = routers.DefaultRouter()
# router.register(r'meetings', MeetingViewSet, base_name='row')
# router.register(r'participants', ParticipantViewSet, base_name='column')
# router.register(r'contributions', ContributionViewSet, base_name='reference')


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/registration/$', registration, name='registration'),
    url(r'^(?P<slug>[-\w]+)/registration/done/$', registration_done, name='registration_done'),
    url(r'^(?P<slug>[-\w]+)/participants/$', participants, name='participants'),
    url(r'^(?P<slug>[-\w]+)/contributions/$', contributions, name='contributions'),

    # rest api
    url(r'^api/', include(router.urls)),
]
