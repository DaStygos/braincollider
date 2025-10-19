from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)