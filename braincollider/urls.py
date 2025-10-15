from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include("core.urls",namespace="core")),
    path("problems/", include("problems.urls",namespace="problems")),
    path("accounts/", include("accounts.urls",namespace="accounts")),
    path("leaderboard/",include("leaderboard.urls",namespace="leaderboard")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

