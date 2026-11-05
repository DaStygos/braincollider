from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ForumAdminShortcutTests(TestCase):
    def test_staff_with_forum_permissions_sees_forum_shortcuts(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin", password="pass", email="admin@example.com"
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Créer un sujet du forum")
        self.assertContains(response, "Gérer les sujets du forum")
        self.assertContains(response, "Gérer les réponses du forum")
        self.assertContains(response, "Gérer les étiquettes du forum")
