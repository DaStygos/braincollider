from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include("core.urls",namespace="core")),
    path("problems/", include("problems.urls",namespace="problems")),
    path("accounts/", include("accounts.urls",namespace="accounts")),
    path("leaderboard/",include("leaderboard.urls",namespace="leaderboard")),
    path("admin/", admin.site.urls),
]

