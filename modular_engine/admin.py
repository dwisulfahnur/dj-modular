from django.contrib import admin
from modular_engine.models import Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_id', 'version', 'status', 'base_path', 'install_date', 'update_date')
    list_filter = ('status',)
    search_fields = ('name', 'module_id', 'description', 'base_path')
    readonly_fields = ('install_date', 'update_date')
