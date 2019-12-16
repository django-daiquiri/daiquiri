from django.urls import include, path
from rest_framework import routers

from .views import (AbstractExportView, EmailExportView, ManagementView,
                    ParticipantExportView, contributions, participants,
                    registration, registration_done)
from .viewsets import (ContributionTypeViewSet, ContributionViewSet,
                       MeetingViewSet, ParticipantViewSet, PaymentViewSet,
                       StatusViewSet)

app_name = 'meetings'

router = routers.DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')
router.register(r'participants', ParticipantViewSet, basename='participant')
router.register(r'contributions', ContributionViewSet, basename='contribution')
router.register(r'contributiontypes', ContributionTypeViewSet, basename='contributiontype')
router.register(r'statuses', StatusViewSet, basename='status')
router.register(r'payments', PaymentViewSet, basename='payment')

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
