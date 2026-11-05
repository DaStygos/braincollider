from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from forum.models import Post, Tag, Topic


class ForumViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice", password="pass")
        self.tag = Tag.objects.create(name="Django", slug="django")

    def test_list_and_detail_are_public(self):
        topic = Topic.objects.create(title="Question", author=self.user)
        self.assertEqual(self.client.get(reverse("forum:topic_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("forum:topic_detail", args=[topic.pk])).status_code, 200)

    def test_create_requires_login_and_supports_optional_tags(self):
        url = reverse("forum:topic_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        self.client.post(url, {"title": "Sans tag", "description": "Premier contexte", "tags": []})
        self.client.post(
            url,
            {
                "title": "Avec tag",
                "description": "Contexte de la question Django",
                "tags": [self.tag.pk],
            },
        )
        self.assertEqual(Topic.objects.count(), 2)
        self.assertEqual(Topic.objects.get(title="Avec tag").tags.get(), self.tag)
        self.assertEqual(
            Topic.objects.get(title="Avec tag").description,
            "Contexte de la question Django",
        )
        self.assertFalse(Post.objects.exists())

    def test_first_message_is_required_when_creating_topic(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("forum:topic_create"),
            {"title": "Sujet sans description", "description": "", "tags": []},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["description"])
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_authenticated_user_can_reply(self):
        topic = Topic.objects.create(title="Question", author=self.user)
        url = reverse("forum:post_create", args=[topic.pk])
        self.assertEqual(self.client.post(url, {"content": "Réponse"}).status_code, 302)
        self.client.force_login(self.user)
        response = self.client.post(url, {"content": "Réponse"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.get().topic, topic)
        self.assertEqual(Post.objects.get().author, self.user)

    def test_topic_detail_does_not_accept_mutations(self):
        topic = Topic.objects.create(title="Question", author=self.user)
        response = self.client.post(reverse("forum:topic_detail", args=[topic.pk]), {"content": "Réponse"})
        self.assertEqual(response.status_code, 405)
        self.assertFalse(Post.objects.exists())

    def test_filter_topics_by_tag(self):
        tagged = Topic.objects.create(title="Avec étiquette", author=self.user)
        tagged.tags.add(self.tag)
        Topic.objects.create(title="Sans étiquette", author=self.user)
        response = self.client.get(reverse("forum:topic_list"), {"tag": "django"})
        self.assertContains(response, "Avec étiquette")
        self.assertNotContains(response, "Sans étiquette")
