from django.contrib import admin

from .models import Proposal


class ProposalAdmin(admin.ModelAdmin):
    search_fields = ['title', 'pi__username', 'copi_username', 'abstract']
    list_display = ['title', 'pi__username', 'proprietary_until', 'phase']


admin.site.register(Proposal, ProposalAdmin)




