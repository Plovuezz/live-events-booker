from django.contrib import admin

from booker.models import Band


@admin.register(Band)
class AdminBand(admin.ModelAdmin):
    pass


