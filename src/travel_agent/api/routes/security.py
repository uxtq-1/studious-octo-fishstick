"""Protected security diagnostic route for integration verification."""

from typing import Annotated

from fastapi import APIRouter, Depends

from travel_agent.security.authorization import CurrentPrincipal, Principal, Role, require_roles

router = APIRouter(prefix="/api/v1/security", tags=["security"])


@router.get("/whoami")
async def whoami(principal: CurrentPrincipal) -> dict[str, str | None]:
    return {
        "userId": principal.user_id,
        "tenantId": principal.tenant_id,
        "role": principal.role.value,
    }


@router.get("/admin-check")
async def admin_check(
    principal: Annotated[
        Principal,
        Depends(require_roles(Role.PLATFORM_OWNER, Role.PLATFORM_ADMIN)),
    ],
) -> dict[str, str]:
    return {"status": "authorized", "userId": principal.user_id}
