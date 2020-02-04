from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_display = ('__str__', 'is_pending', 'is_confirmed')
    list_filter = ('is_pending', 'is_confirmed', 'user__is_staff', 'user__is_superuser')
    readonly_fields = ('user', 'consent')


admin.site.register(Profile, ProfileAdmin)
