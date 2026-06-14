"""Small process-local limiter for the development foundation.

Production deployments should replace this store with a shared edge or durable
limiter so limits are consistent across instances.
"""

import time
from collections import defaultdict, deque
from collections.abc import Callable

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

LIMITED_PATH_PREFIXES = (
    "/api/v1/auth",
    "/api/v1/bookings",
    "/api/v1/payments",
    "/api/v1/search",
    "/api/v1/tickets",
    "/api/v1/security",
)


class RateLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        requests: int = 60,
        window_seconds: int = 60,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.app = app
        self.requests = requests
        self.window_seconds = window_seconds
        self.clock = clock
        self._requests: defaultdict[str, deque[float]] = defaultdict(deque)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not scope["path"].startswith(LIMITED_PATH_PREFIXES):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        client = scope.get("client")
        client_host = client[0] if client else "unknown"
        subject = headers.get("authorization", client_host)
        key = f"{scope['path']}:{subject}"
        now = self.clock()
        entries = self._requests[key]
        cutoff = now - self.window_seconds
        while entries and entries[0] <= cutoff:
            entries.popleft()
        if len(entries) >= self.requests:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(self.window_seconds)},
            )
            await response(scope, receive, send)
            return
        entries.append(now)
        await self.app(scope, receive, send)
