from django.contrib import admin
from .models import BuilderSnapshot, CustomContentType, CustomField, CustomEntry


class CustomFieldInline(admin.TabularInline):
    model = CustomField
    extra = 1
    fields = ('name', 'slug', 'field_type', 'required', 'unique', 'order', 'config')


@admin.register(CustomContentType)
class CustomContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'icon', 'config', 'is_active')
    inlines = [CustomFieldInline]


@admin.register(CustomEntry)
class CustomEntryAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'is_published', 'updated_at')
    list_filter = ('content_type', 'is_published')
    search_fields = ('data',)


@admin.register(BuilderSnapshot)
class BuilderSnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_auto', 'created_by', 'created_at')
    list_filter = ('is_auto', 'created_at')
    search_fields = ('name', 'note')
    readonly_fields = ('schema', 'created_at')
