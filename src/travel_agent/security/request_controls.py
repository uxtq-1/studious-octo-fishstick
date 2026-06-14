"""Request size, method, and media-type enforcement."""

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH"})
JSON_CONTENT_TYPES = frozenset({"application/json", "application/problem+json"})


class RequestControlsMiddleware:
    def __init__(self, app: ASGIApp, *, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"].upper()
        path = scope["path"]
        headers = Headers(scope=scope)
        content_length = headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    await self._reject(scope, receive, send, 413, "Request body too large")
                    return
            except ValueError:
                await self._reject(scope, receive, send, 400, "Invalid request")
                return

        if path.startswith("/api/") and method in MUTATING_METHODS:
            media_type = headers.get("content-type", "").split(";", 1)[0].lower()
            if media_type not in JSON_CONTENT_TYPES:
                await self._reject(scope, receive, send, 415, "Unsupported media type")
                return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    return {"type": "http.disconnect"}
            return message

        await self.app(scope, limited_receive, send)

    @staticmethod
    async def _reject(
        scope: Scope,
        receive: Receive,
        send: Send,
        status_code: int,
        detail: str,
    ) -> None:
        response = JSONResponse(status_code=status_code, content={"detail": detail})
        await response(scope, receive, send)
