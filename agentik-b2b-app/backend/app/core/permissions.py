PERMISSIONS = {
    "buyer": [
        "rfq:create", "rfq:read", "rfq:update", "rfq:delete",
        "supplier:read", "quote:read", "order:create"
    ],
    "supplier": [
        "rfq:read", "quote:create", "quote:update",
        "catalog:manage", "profile:update"
    ],
    "admin": ["*"],
    "manager": [
        "rfq:read", "rfq:approve", "user:manage",
        "analytics:read", "report:generate"
    ]
}

def has_permission(role: str, permission: str) -> bool:
    perms = PERMISSIONS.get(role, [])
    return "*" in perms or permission in perms

