from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Notification
from .forms import BroadcastNotificationForm


class NotificationsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reader", password="password123")
        self.other_user = User.objects.create_user(
            username="other", password="password123"
        )

    def test_notifications_list_requires_login(self):
        response = self.client.get(reverse("notifications:notifications_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_notifications_list_separates_read_and_unread(self):
        unread_newer = Notification.objects.create(
            user=self.user, message="Unread newer"
        )
        unread_older = Notification.objects.create(
            user=self.user, message="Unread older"
        )
        read_notification = Notification.objects.create(
            user=self.user, message="Read note", read=True
        )
        Notification.objects.filter(pk=unread_newer.pk).update(
            created_at=timezone.now()
        )
        Notification.objects.filter(pk=unread_older.pk).update(
            created_at=timezone.now() - timedelta(minutes=1)
        )
        Notification.objects.filter(pk=read_notification.pk).update(
            created_at=timezone.now() - timedelta(minutes=2)
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:notifications_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["unread_count"], 2)
        self.assertContains(
            response, 'class="list-group-item notification-item notification-item-unread"'
        )
        self.assertContains(
            response, 'class="list-group-item notification-item notification-item-read"'
        )
        self.assertContains(response, "À lire")
        self.assertContains(response, "Déjà lues")
        self.assertEqual(
            [
                notification.message
                for notification in response.context["unread_notifications"]
            ],
            ["Unread newer", "Unread older"],
        )
        self.assertEqual(
            [
                notification.message
                for notification in response.context["read_notifications"]
            ],
            ["Read note"],
        )

    def test_mark_as_read_marks_only_own_notification(self):
        notification = Notification.objects.create(user=self.user, message="Mark me")
        Notification.objects.create(user=self.other_user, message="Other note")

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("notifications:mark_as_read", args=[notification.pk]), follow=True
        )

        self.assertEqual(response.redirect_chain[-1][0], reverse("notifications:notifications_list"))
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        self.assertContains(response, "La notification a été marquée comme lue.")

    def test_notifications_list_links_notifications_with_redirect_url(self):
        Notification.objects.create(
            user=self.user,
            message="Problem solved",
            redirect_url="/problems/42/",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:notifications_list"))

        self.assertContains(
            response, '<a href="/problems/42/">Problem solved</a>', html=True
        )

    def test_notifications_list_shows_empty_state_when_there_are_no_unread_items(self):
        Notification.objects.create(user=self.user, message="Already read", read=True)
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications:notifications_list"))

        self.assertContains(response, "Vous êtes à jour. Aucune notification à lire.")
        self.assertContains(response, "Déjà lues")
        self.assertNotContains(response, "Tout marquer comme lu")

    def test_notifications_list_hides_read_section_when_history_is_empty(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications:notifications_list"))

        self.assertContains(response, "Vous êtes à jour. Aucune notification à lire.")
        self.assertNotContains(response, "Déjà lues")

    def test_mark_all_as_read_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications:mark_all_as_read"))

        self.assertEqual(response.status_code, 405)


class BroadcastNotificationAdminTests(TestCase):
    def test_broadcast_form_rejects_external_and_javascript_urls(self):
        for url in ("javascript:alert(1)", "https://example.com/", "//example.com/"):
            with self.subTest(url=url):
                form = BroadcastNotificationForm(
                    {"message": "Hello", "redirect_url": url}
                )
                self.assertFalse(form.is_valid())

    def test_broadcast_form_accepts_local_paths(self):
        form = BroadcastNotificationForm(
            {"message": "Hello", "redirect_url": "/groups/"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["redirect_url"], "/groups/")

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )
        self.member = User.objects.create_user(
            username="member", password="password123"
        )

    def test_broadcast_form_is_available_in_admin(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("admin:notifications_notification_send_to_all")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Envoyer une notification à tous les membres")

    def test_broadcast_creates_one_notification_per_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:notifications_notification_send_to_all"),
            {
                "message": "Maintenance prévue ce soir.",
                "redirect_url": "/groups/",
            },
        )

        self.assertRedirects(response, reverse("admin:index"))
        self.assertEqual(
            Notification.objects.filter(message="Maintenance prévue ce soir.").count(),
            2,
        )
        self.assertEqual(
            Notification.objects.filter(
                message="Maintenance prévue ce soir.",
                redirect_url="/groups/",
            ).count(),
            2,
        )
