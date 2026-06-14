"""Browser security headers and request correlation middleware."""

from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
    )
)


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp, *, enable_hsts: bool) -> None:
        self.app = app
        self.enable_hsts = enable_hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
                headers["Cross-Origin-Opener-Policy"] = "same-origin"
                # credentialless is safer for compatibility than require-corp
                # while still isolating cross-origin no-CORS resources.
                headers["Cross-Origin-Embedder-Policy"] = "credentialless"
                headers["Cross-Origin-Resource-Policy"] = "same-origin"
                headers["Permissions-Policy"] = (
                    "geolocation=(), camera=(), microphone=(), payment=()"
                )
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["X-Request-Id"] = request_id
                if self.enable_hsts:
                    headers["Strict-Transport-Security"] = (
                        "max-age=31536000; includeSubDomains; preload"
                    )
            await send(message)

        await self.app(scope, receive, send_with_headers)


async def safe_http_exception_handler(request: Request, exc: Exception) -> Response:
    from fastapi import HTTPException
    from fastapi.responses import JSONResponse

    if isinstance(exc, HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "Invalid request"
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail, "requestId": request.state.request_id},
            headers=exc.headers,
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "requestId": request.state.request_id},
    )
