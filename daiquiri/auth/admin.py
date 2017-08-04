from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('__str__', )
    list_display = ('__str__', 'is_pending', 'is_confirmed')
    readonly_fields = ('user', )

admin.site.register(Profile, ProfileAdmin)
