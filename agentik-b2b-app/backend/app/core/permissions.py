from fastapi import Depends, HTTPException, status
from typing import Any, Dict
from app.core.auth import get_current_user_profile

PERMISSIONS = {
    "buyer": [
        "rfq:create", "rfq:read", "rfq:update", "rfq:delete",
        "supplier:read", "quote:read", "order:create",
        "notifications:read", "notifications:write",
        "email:read", "email:send",
        "verification:request"
    ],
    "supplier": [
        "rfq:read", "quote:create", "quote:update", "quote:read",
        "catalog:manage", "profile:update", "notifications:read",
        "verification:request"
    ],
    "admin": ["*"],
    "manager": [
        "rfq:read", "rfq:approve", "user:manage",
        "analytics:read", "report:generate", "notifications:read", "email:read",
        "verification:review"
    ]
}

def has_permission(role: str, permission: str) -> bool:
    perms = PERMISSIONS.get(role, [])
    return "*" in perms or permission in perms

def require_permission(permission: str):
    async def _checker(user: Dict[str, Any] = Depends(get_current_user_profile)):
        role = user.get("role") or user.get("role_name") or user.get("user_role")
        if not role or not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return True
    return _checker
