from django.contrib import admin
from .models import InstalledModule


@admin.register(InstalledModule)
class InstalledModuleAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'enabled', 'version', 'updated_at')
    list_filter = ('enabled',)
    search_fields = ('label', 'name', 'description')
