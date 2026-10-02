from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from .models import Notification
from .forms import BroadcastNotificationForm

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'send-to-all/',
                self.admin_site.admin_view(self.send_to_all_view),
                name='notifications_notification_send_to_all',
            ),
        ]
        return custom_urls + urls

    def send_to_all_view(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == 'POST':
            form = BroadcastNotificationForm(request.POST)
            if form.is_valid():
                users = get_user_model().objects.all().only('pk')
                notifications = [
                    Notification(user_id=user.pk, message=form.cleaned_data['message'])
                    for user in users
                ]
                with transaction.atomic():
                    Notification.objects.bulk_create(notifications)
                self.message_user(request, f'{len(notifications)} notification(s) envoyée(s).')
                return HttpResponseRedirect(reverse('admin:index'))
        else:
            form = BroadcastNotificationForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Envoyer une notification à tous les membres',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/notifications/send_to_all.html', context)