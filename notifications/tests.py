from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Notification


class NotificationsViewsTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="reader", password="password123")
		self.other_user = User.objects.create_user(username="other", password="password123")

	def test_notifications_list_requires_login(self):
		response = self.client.get(reverse("notifications:notifications_list"))

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("accounts:login"), response.url)

	def test_notifications_list_separates_read_and_unread(self):
		unread_newer = Notification.objects.create(user=self.user, message="Unread newer")
		unread_older = Notification.objects.create(user=self.user, message="Unread older")
		read_notification = Notification.objects.create(user=self.user, message="Read note", read=True)
		Notification.objects.filter(pk=unread_newer.pk).update(created_at=timezone.now())
		Notification.objects.filter(pk=unread_older.pk).update(created_at=timezone.now() - timedelta(minutes=1))
		Notification.objects.filter(pk=read_notification.pk).update(created_at=timezone.now() - timedelta(minutes=2))

		self.client.force_login(self.user)
		response = self.client.get(reverse("notifications:notifications_list"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["unread_count"], 2)
		self.assertEqual(
			[notification.message for notification in response.context["unread_notifications"]],
			["Unread newer", "Unread older"],
		)
		self.assertEqual(
			[notification.message for notification in response.context["read_notifications"]],
			["Read note"],
		)

	def test_mark_as_read_marks_only_own_notification(self):
		notification = Notification.objects.create(user=self.user, message="Mark me")
		Notification.objects.create(user=self.other_user, message="Other note")

		self.client.force_login(self.user)
		response = self.client.get(reverse("notifications:mark_as_read", args=[notification.pk]))

		self.assertRedirects(response, reverse("notifications:notifications_list"))
		notification.refresh_from_db()
		self.assertTrue(notification.read)
