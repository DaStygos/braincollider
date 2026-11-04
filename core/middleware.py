import secrets


class ContentSecurityPolicyMiddleware:
    """Set a per-response nonce for inline scripts and a restrictive CSP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(18)
        response = self.get_response(request)
        nonce = request.csp_nonce
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net 'nonce-{nonce}'; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data: https://cdn.jsdelivr.net; "
            "connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
        return response
