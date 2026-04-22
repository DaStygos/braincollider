from django.test import TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):
	def test_home_page_loads(self):
		response = self.client.get(reverse("core:home"))

		self.assertEqual(response.status_code, 200)
