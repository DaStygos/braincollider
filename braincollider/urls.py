from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from braincollider.sitemaps import StaticViewSitemap, ProblemSitemap
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'problems': ProblemSitemap,
}

urlpatterns = [
    path('', include("core.urls",namespace="core")),
    path("problems/", include("problems.urls",namespace="problems")),
    path("accounts/", include("accounts.urls",namespace="accounts")),
    path("leaderboard/",include("leaderboard.urls",namespace="leaderboard")),
    path("statistics/", include("stats.urls", namespace="stats")),
    path("groups/", include("groups.urls", namespace="groups")),
    path("admin/", admin.site.urls),
    path("notifications/", include("notifications.urls",namespace="notifications")),
    path("staff/", include("staff.urls", namespace="staff")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),name="robots_file",),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.views.error_400"
handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"

