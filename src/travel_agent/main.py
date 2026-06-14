"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from travel_agent.api.routes.health import router as health_router
from travel_agent.config import Settings, get_settings
from travel_agent.policy.loader import load_policy

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
    app.include_router(health_router)
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
