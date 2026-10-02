from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from problems.models import Problem


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'leaderboard:leaderboard', 'problems:index']

    def location(self, item):
        return reverse(item)


class ProblemSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return Problem.objects.all()

    def location(self, obj):
        return reverse('problems:problem_detail', args=[obj.pk])