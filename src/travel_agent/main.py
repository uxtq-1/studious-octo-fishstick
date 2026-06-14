"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from travel_agent.api.routes.health import router as health_router
from travel_agent.api.routes.security import router as security_router
from travel_agent.config import Settings, get_settings
from travel_agent.policy.loader import load_policy
from travel_agent.security.headers import SecurityHeadersMiddleware, safe_http_exception_handler
from travel_agent.security.rate_limit import RateLimitMiddleware
from travel_agent.security.request_controls import RequestControlsMiddleware

PACKAGE_ROOT = Path(__file__).parent
TEMPLATES = Jinja2Templates(directory=PACKAGE_ROOT / "templates")


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.policy = load_policy(app_settings.policy_path)
        yield

    app = FastAPI(
        title=app_settings.app_name,
        version="0.1.0",
        description="Demonstration only: no real reservations or card payments.",
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.add_exception_handler(HTTPException, safe_http_exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Authorization",
            "Content-Type",
            "X-CSRF-Token",
            "X-Request-Id",
            "X-Session-Id",
            "X-Tenant-Id",
        ],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=app_settings.allowed_hosts)
    app.add_middleware(
        RequestControlsMiddleware,
        max_body_bytes=app_settings.max_request_body_bytes,
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=app_settings.environment == "production",
    )
    app.include_router(health_router)
    app.include_router(security_router)
    app.mount("/static", StaticFiles(directory=PACKAGE_ROOT / "static"), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home(request: Request) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="trips/index.html",
            context={"simulation_mode": app_settings.simulation_mode},
        )

    return app


app = create_app()


def run() -> None:
    uvicorn.run("travel_agent.main:app", host="127.0.0.1", port=8000, reload=True)
