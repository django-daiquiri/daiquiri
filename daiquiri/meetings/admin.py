from django.contrib import admin

from .models import Meeting, Participant, Contribution


class MeetingAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('title', 'slug', 'registration_open', 'participants_open', 'contributions_open')


class ParticipantAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('full_name', 'email', 'meeting', 'accepted')


class ContributionAdmin(admin.ModelAdmin):
    search_fields = ('title', 'participant__first_name', 'participant__last_name')
    list_display = ('title', 'participant', 'contribution_type', 'accepted')


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Contribution, ContributionAdmin)
