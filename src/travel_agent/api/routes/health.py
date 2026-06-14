"""Operational health endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/health/startup")
async def startup() -> dict[str, str]:
    return {"status": "started"}
