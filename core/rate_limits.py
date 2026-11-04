"""Small cache-backed fixed-window rate limits for public endpoints."""

from functools import wraps
from hashlib import sha256
from time import time

from django.core.cache import cache
from django.http import HttpResponse


def rate_limit(name, limit, period, methods=None):
    """Limit requests per client IP; use a shared cache in multi-worker deploys."""

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if methods and request.method not in methods:
                return view(request, *args, **kwargs)
            client_ip = request.META.get("REMOTE_ADDR", "unknown")
            bucket = int(time() // period)
            digest = sha256(client_ip.encode("utf-8")).hexdigest()
            key = f"rate-limit:{name}:{digest}:{bucket}"

            if not cache.add(key, 1, timeout=period + 1):
                try:
                    count = cache.incr(key)
                except ValueError:
                    cache.add(key, 1, timeout=period + 1)
                    count = 1
            else:
                count = 1

            if count > limit:
                response = HttpResponse(
                    "Too many requests. Please try again later.", status=429
                )
                response["Retry-After"] = str(period - (int(time()) % period))
                return response
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
