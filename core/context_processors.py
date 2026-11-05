from django.conf import settings


def seo_metadata(request):
    path = request.path
    noindex_prefixes = (
        "/accounts/",
        "/groups/",
        "/notifications/",
        "/staff/",
        "/admin/",
        "/statistics/",
    )
    noindex = settings.DEBUG or path.startswith(noindex_prefixes)

    if path.startswith("/forum/topics/new/") or path.endswith("/reply/"):
        noindex = True
    if path == "/forum/" and request.GET:
        noindex = True
    if path.startswith("/forum/topics/") and request.GET.get("posts"):
        noindex = True
    if path == "/problems/" and request.GET:
        noindex = True
    if path == "/leaderboard/" and request.GET.get("page"):
        noindex = True

    return {
        "site_url": settings.SITE_URL,
        "canonical_url": f"{settings.SITE_URL}{path}",
        "robots_meta": "noindex, follow" if noindex else "index, follow",
    }
