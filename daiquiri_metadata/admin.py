from django.contrib import admin

from .models import Database, Table, Column, Function

admin.site.register(Database)
admin.site.register(Table)
admin.site.register(Column)
admin.site.register(Function)
