from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from problems.models import Problem


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return ["core:home", "leaderboard:leaderboard", "problems:index"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {
            "core:home": 1.0,
            "problems:index": 0.9,
            "leaderboard:leaderboard": 0.4,
        }.get(item, 0.3)

    def changefreq(self, item):
        if item in {"core:home", "problems:index"}:
            return "weekly"
        return "monthly"


class ProblemSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Problem.objects.all()

    def location(self, obj):
        return reverse("problems:problem_detail", args=[obj.pk])
