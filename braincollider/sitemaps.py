from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from forum.models import Topic
from problems.models import Problem


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "problems:index",
            "forum:topic_list",
            "leaderboard:leaderboard",
            "core:contact",
            "core:legal_notice",
            "core:privacy",
            "core:terms",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {
            "core:home": 1.0,
            "problems:index": 0.9,
            "forum:topic_list": 0.7,
            "leaderboard:leaderboard": 0.4,
        }.get(item, 0.3)

    def changefreq(self, item):
        if item in {"core:home", "problems:index", "forum:topic_list"}:
            return "weekly"
        return "monthly"


class ProblemSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"
    lastmod = "updated_at"

    def items(self):
        return Problem.objects.all()

    def location(self, obj):
        return reverse("problems:problem_detail", args=[obj.pk])


class ForumTopicSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"
    lastmod = "updated_at"

    def items(self):
        return Topic.objects.exclude(description="").order_by("-updated_at")

    def location(self, obj):
        return reverse("forum:topic_detail", args=[obj.pk])
