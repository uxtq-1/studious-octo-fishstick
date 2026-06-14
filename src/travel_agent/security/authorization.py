"""Identity, role, tenant, and ownership authorization primitives."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status


class Role(StrEnum):
    PLATFORM_OWNER = "platform_owner"
    PLATFORM_ADMIN = "platform_admin"
    SECURITY_OPS_ADMIN = "security_ops_admin"
    TENANT_OWNER = "tenant_owner"
    TENANT_STAFF = "tenant_staff"
    SUPPORT_L1 = "support_l1"
    SUPPORT_L2 = "support_l2"
    SUPPORT_L3 = "support_l3"
    FINANCE_BILLING = "finance_billing"
    END_CONSUMER = "end_consumer"
    AUDITOR = "auditor"


PLATFORM_ROLES = frozenset({Role.PLATFORM_OWNER, Role.PLATFORM_ADMIN, Role.SECURITY_OPS_ADMIN})


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    role: Role
    tenant_id: str | None = None


def _safe_auth_error(status_code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=detail)


async def authenticated_principal(request: Request) -> Principal:
    """Resolve a principal.

    The header authenticator is deliberately development-only. Production must
    replace it with verified OIDC/Firebase token middleware that sets
    ``request.state.principal``.
    """

    principal = getattr(request.state, "principal", None)
    if isinstance(principal, Principal):
        return principal

    settings = request.app.state.settings
    if not settings.dev_auth_enabled or settings.environment == "production":
        raise _safe_auth_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

    user_id = request.headers.get("X-Debug-User-Id")
    role_value = request.headers.get("X-Debug-Role")
    if not user_id or not role_value:
        raise _safe_auth_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    try:
        role = Role(role_value)
    except ValueError as exc:
        raise _safe_auth_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized") from exc
    return Principal(
        user_id=user_id,
        role=role,
        tenant_id=request.headers.get("X-Debug-Tenant-Id"),
    )


CurrentPrincipal = Annotated[Principal, Depends(authenticated_principal)]


def require_roles(*allowed_roles: Role):
    allowed = frozenset(allowed_roles)

    async def dependency(principal: CurrentPrincipal) -> Principal:
        if principal.role not in allowed:
            raise _safe_auth_error(status.HTTP_403_FORBIDDEN, "Forbidden")
        return principal

    return dependency


def authorize_resource(
    principal: Principal,
    *,
    owner_user_id: str | None,
    tenant_id: str | None,
    admin_roles: frozenset[Role] = PLATFORM_ROLES,
) -> None:
    if principal.role in admin_roles:
        return
    if owner_user_id and principal.user_id == owner_user_id:
        return
    if tenant_id and principal.tenant_id and principal.tenant_id == tenant_id:
        return
    raise _safe_auth_error(status.HTTP_403_FORBIDDEN, "Forbidden")
