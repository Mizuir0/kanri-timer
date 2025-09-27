from django.contrib import admin
from .models import Band, Timer

@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    list_display = ['name', 'band', 'duration_minutes', 'order', 'is_active']
    list_filter = ['band', 'is_active', 'created_at']
    search_fields = ['name', 'band__name']
    list_editable = ['order', 'is_active']  # 一覧画面で直接編集可能
    
    fieldsets = (
        ('基本情報', {
            'fields': ('band', 'name', 'duration_minutes', 'order', 'is_active')
        }),
        ('管理者情報', {
            'fields': ('manager1', 'manager2', 'manager3'),
            'classes': ('collapse',)  # 折りたたみ可能
        }),
    )