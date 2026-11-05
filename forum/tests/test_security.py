from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from forum.forms import PostForm, TopicForm
from forum.models import Post, Topic


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "forum-security-tests",
        }
    }
)
class ForumSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            username="writer", password="password"
        )
        self.topic = Topic.objects.create(
            title="Question", description="Contexte", author=self.user
        )
        self.client.force_login(self.user)

    def test_topic_creation_is_rate_limited(self):
        url = reverse("forum:topic_create")
        data = {"title": "Question", "description": "Contexte", "tags": []}

        for _ in range(5):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 302)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 429)

    def test_reply_limit_blocks_excess_posts(self):
        reply_url = reverse("forum:post_create", args=[self.topic.pk])

        for _ in range(30):
            self.assertEqual(
                self.client.post(reply_url, {"content": "Une réponse."}).status_code,
                302,
            )

        response = self.client.post(reply_url, {"content": "Une réponse de trop."})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Post.objects.count(), 30)

    def test_reply_content_has_a_maximum_length(self):
        form = PostForm({"content": "x" * 20001})

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_topic_description_has_a_maximum_length(self):
        form = TopicForm(
            {"title": "Long", "description": "x" * 10001, "tags": []}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_authenticated_mutations_require_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(
            reverse("forum:topic_create"),
            {"title": "Forged", "description": "Forged", "tags": []},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Topic.objects.filter(title="Forged").exists())

    def test_topic_list_is_paginated(self):
        Topic.objects.bulk_create(
            [
                Topic(title=f"Question {index}", author=self.user)
                for index in range(26)
            ]
        )

        response = self.client.get(reverse("forum:topic_list"), {"page": "2"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["topic_count"], 27)
        self.assertEqual(len(response.context["topics"]), 2)

    def test_replies_are_paginated(self):
        Post.objects.bulk_create(
            [
                Post(topic=self.topic, author=self.user, content=f"Reply {index}")
                for index in range(51)
            ]
        )

        response = self.client.get(
            reverse("forum:topic_detail", args=[self.topic.pk]), {"posts": "2"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["post_count"], 51)
        self.assertEqual(len(response.context["posts"]), 1)

    def test_forum_search_escapes_user_content(self):
        Topic.objects.create(
            title="Security <script>alert(1)</script>",
            description="Context",
            author=self.user,
        )

        response = self.client.get(
            reverse("accounts:user_search"), {"q": "Security"}
        )

        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_topic_and_replies_escape_stored_markup(self):
        self.topic.description = "<script>alert('description')</script>"
        self.topic.save(update_fields=["description"])
        Post.objects.create(
            topic=self.topic,
            author=self.user,
            content="<img src=x onerror=alert('reply')>",
        )

        response = self.client.get(reverse("forum:topic_detail", args=[self.topic.pk]))

        self.assertContains(response, "&lt;script&gt;alert(&#x27;description&#x27;)&lt;/script&gt;")
        self.assertContains(response, "&lt;img src=x onerror=alert(&#x27;reply&#x27;)&gt;")
        self.assertNotContains(response, "<script>alert('description')</script>")
        self.assertNotContains(response, "<img src=x onerror=alert('reply')>")

    def test_global_search_caps_query_length(self):
        response = self.client.get(
            reverse("accounts:user_search"), {"q": "x" * 150}
        )

        self.assertEqual(len(response.context["query"]), 100)
