from django.urls import include, path

from rest_framework import routers

from .views import (
    registration,
    registration_done,
    participants,
    contributions,
    ManagementView,
    ParticipantExportView,
    AbstractExportView,
    EmailExportView
)
from .viewsets import (
    MeetingViewSet,
    ParticipantViewSet,
    ContributionViewSet,
    ContributionTypeViewSet,
    StatusViewSet,
    PaymentViewSet
)


app_name = 'meetings'

router = routers.DefaultRouter()
router.register(r'meetings', MeetingViewSet, base_name='meeting')
router.register(r'participants', ParticipantViewSet, base_name='participant')
router.register(r'contributions', ContributionViewSet, base_name='contribution')
router.register(r'contributiontypes', ContributionTypeViewSet, base_name='contributiontype')
router.register(r'statuses', StatusViewSet, base_name='status')
router.register(r'payments', PaymentViewSet, base_name='payment')

urlpatterns = [
    path('api/', include(router.urls)),
    path('<slug:slug>/registration/', registration, name='registration'),
    path('<slug:slug>/registration/done/', registration_done, name='registration_done'),
    path('<slug:slug>/participants/', participants, name='participants'),
    path('<slug:slug>/contributions/', contributions, name='contributions'),
    path('<slug:slug>/management/', ManagementView.as_view(), name='management'),
    path('<slug:slug>/export/participants/<slug:format>/', ParticipantExportView.as_view(), name='export_participants'),
    path('<slug:slug>/export/abstracts/', AbstractExportView.as_view(), name='export_abstracts'),
    path('<slug:slug>/export/emails/', EmailExportView.as_view(), name='export_emails'),
]
