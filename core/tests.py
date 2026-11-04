from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from problems.models import Problem, Submission
from core.templatetags.custom_tags import linebreaks_preserve_latex
from core.rate_limits import rate_limit


class CoreViewsTests(TestCase):
    def test_pages_send_nonce_based_content_security_policy(self):
        response = self.client.get(reverse("core:home"))
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
        self.assertIn("object-src 'none'", response["Content-Security-Policy"])
        self.assertIn(
            "script-src 'self' https://cdn.jsdelivr.net 'nonce-",
            response["Content-Security-Policy"],
        )
        nonce = (
            response["Content-Security-Policy"].split("'nonce-", 1)[1].split("'", 1)[0]
        )
        self.assertIn(f'nonce="{nonce}"', body)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_linebreaks_preserve_latex_escapes_html(self):
        result = linebreaks_preserve_latex(
            "<script>alert(1)</script>\n$<img src=x onerror=alert(1)>$"
        )

        self.assertEqual(
            str(result),
            "&lt;script&gt;alert(1)&lt;/script&gt;<br>$&lt;img src=x onerror=alert(1)&gt;$",
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La physique commence par")
        self.assertContains(response, 'class="home-visual"')

    def test_home_page_links_to_each_problem_category(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(len(response.context["problem_categories"]), 6)
        self.assertContains(response, "?category=meca")
        self.assertContains(response, "Mécanique")
        self.assertContains(response, "Électromagnétisme")

    def test_home_page_exposes_live_platform_metrics(self):
        problem = Problem.objects.create(
            title="Problem",
            statement="Statement",
            solution="Solution",
        )
        user = User.objects.create_user(username="solver", password="password")
        Submission.objects.create(
            user=user,
            problem=problem,
            answer="Answer",
            is_correct=True,
        )

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            response.context["home_metrics"],
            {
                "problem_count": 1,
                "accepted_submission_count": 1,
                "solving_member_count": 1,
            },
        )
        self.assertNotContains(response, "120+")
        self.assertNotContains(response, "+12%")
        self.assertNotContains(response, "#14")

    @override_settings(DEBUG=False)
    def test_unknown_url_renders_not_found_page(self):
        response = self.client.get("/url-inconnue/", follow=False)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")
        self.assertContains(response, "Page introuvable", status_code=404)

    @override_settings(DEBUG=False)
    def test_unknown_problem_url_identifies_problem(self):
        user = User.objects.create_user(username="tester", password="password")
        self.client.force_login(user)

        response = self.client.get("/problems/140/", follow=False)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Problème introuvable", status_code=404)

    @override_settings(DEBUG=False)
    def test_unknown_user_url_identifies_user(self):
        response = self.client.get("/accounts/u/inconnu/", follow=False)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Utilisateur introuvable", status_code=404)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "core-rate-limit-tests",
        }
    }
)
class RateLimitTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.request_factory = RequestFactory()

    def test_rate_limit_returns_429_after_configured_limit(self):
        @rate_limit("test", limit=2, period=60)
        def view(request):
            from django.http import HttpResponse

            return HttpResponse("ok")

        responses = [
            view(self.request_factory.get("/", REMOTE_ADDR="192.0.2.1"))
            for _ in range(3)
        ]
        self.assertEqual(
            [response.status_code for response in responses], [200, 200, 429]
        )
        self.assertGreaterEqual(int(responses[-1]["Retry-After"]), 1)
        self.assertLessEqual(int(responses[-1]["Retry-After"]), 60)

    def test_post_only_rate_limit_does_not_count_get_requests(self):
        @rate_limit("post-only-test", limit=1, period=60, methods={"POST"})
        def view(request):
            from django.http import HttpResponse

            return HttpResponse("ok")

        get_response = view(self.request_factory.get("/", REMOTE_ADDR="192.0.2.2"))
        post_response = view(self.request_factory.post("/", REMOTE_ADDR="192.0.2.2"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)
