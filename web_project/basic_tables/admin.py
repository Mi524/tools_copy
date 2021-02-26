from django.contrib import admin

from .models import TestModule, BasicCountry, UndertakeTeam

admin.site.register(BasicCountry)
admin.site.register(TestModule)
admin.site.register(UndertakeTeam)
