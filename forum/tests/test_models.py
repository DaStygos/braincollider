from django.contrib.auth import get_user_model
from django.test import TestCase

from forum.models import Post, Tag, Topic


class ForumModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice", password="pass")
        self.topic = Topic.objects.create(title="Bienvenue", author=self.user)

    def test_tag_string_and_topic_tag_relation(self):
        tag = Tag.objects.create(name="Django", slug="django")
        self.topic.tags.add(tag)
        self.assertEqual(str(tag), "Django")
        self.assertIn(tag, self.topic.tags.all())
        self.assertIn(self.topic, tag.topics.all())

    def test_topic_and_post_strings_and_relation(self):
        post = Post.objects.create(topic=self.topic, author=self.user, content="Bonjour")
        self.assertEqual(str(self.topic), "Bienvenue")
        self.assertIn(post, self.topic.posts.all())
        self.assertEqual(post.topic, self.topic)
        self.assertIn("alice", str(post))
