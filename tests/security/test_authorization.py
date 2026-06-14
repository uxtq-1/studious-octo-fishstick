import pytest
from fastapi import HTTPException

from travel_agent.security.authorization import Permission, Principal, Role, authorize_resource


def test_owner_can_access_resource():
    principal = Principal(user_id="user-1", role=Role.END_CONSUMER, tenant_id=None)
    authorize_resource(principal, owner_user_id="user-1", tenant_id=None)


def test_tenant_cannot_access_another_tenant():
    principal = Principal(user_id="staff-1", role=Role.TENANT_STAFF, tenant_id="tenant-a")
    with pytest.raises(HTTPException) as error:
        authorize_resource(principal, owner_user_id=None, tenant_id="tenant-b")
    assert error.value.status_code == 403


def test_platform_admin_has_explicit_admin_access():
    principal = Principal(user_id="admin-1", role=Role.PLATFORM_ADMIN)
    authorize_resource(principal, owner_user_id="another-user", tenant_id="tenant-b")


def test_consumer_cannot_inherit_tenant_wide_access():
    principal = Principal(user_id="user-1", role=Role.END_CONSUMER, tenant_id="tenant-a")
    with pytest.raises(HTTPException):
        authorize_resource(
            principal,
            owner_user_id="user-2",
            tenant_id="tenant-a",
            permission=Permission.BOOKING_READ,
        )


def test_role_requires_explicit_action_permission():
    principal = Principal(user_id="auditor-1", role=Role.AUDITOR, tenant_id="tenant-a")
    with pytest.raises(HTTPException):
        authorize_resource(
            principal,
            owner_user_id=None,
            tenant_id="tenant-a",
            permission=Permission.REFUND_APPROVE,
        )
