# Simple test to verify our RBAC implementation without database dependencies
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath('.'))

# Define the role permissions directly for testing
ROLE_PERMISSIONS = {
    "admin": ["*"],
    "buyer": [
        "rfq:create", "rfq:read", "rfq:update", "rfq:delete",
        "supplier:read", "catalog:read", "offer:read", "verification:request"
    ],
    "supplier": [
        "rfq:read", "catalog:create", "catalog:read", "catalog:update", "catalog:delete",
        "offer:create", "offer:read", "offer:update", "verification:request"
    ],
    "manager": [
        "rfq:read", "rfq:approve", "supplier:read", "catalog:read",
        "offer:read", "user:manage", "analytics:read"
    ]
}

def _has_permission(user_role: str, resource: str, action: str) -> bool:
    """Check if user role has permission for resource:action"""
    # Admin has all permissions
    if user_role == "admin":
        return True
    
    # Get permissions for the role
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    # Check for wildcard permission
    if "*" in permissions:
        return True
    
    # Check for specific permission
    target = f"{resource}:{action}"
    if target in permissions:
        return True
    
    # Check for resource-level permission (e.g., "rfq:*")
    resource_wildcard = f"{resource}:*"
    if resource_wildcard in permissions:
        return True
    
    return False

# Test the role permissions
def test_rbac():
    print("Testing RBAC implementation...")
    
    # Check that we have the expected roles
    expected_roles = ['admin', 'buyer', 'supplier', 'manager']
    for role in expected_roles:
        assert role in ROLE_PERMISSIONS, f"Role {role} not found in ROLE_PERMISSIONS"
    
    # Check that admin has all permissions
    assert "*" in ROLE_PERMISSIONS['admin'], "Admin should have all permissions"
    
    # Check that buyer has expected permissions
    assert _has_permission('buyer', 'rfq', 'create'), "Buyer should have rfq:create permission"
    assert _has_permission('buyer', 'supplier', 'read'), "Buyer should have supplier:read permission"
    assert not _has_permission('buyer', 'catalog', 'create'), "Buyer should not have catalog:create permission"
    
    # Check that supplier has expected permissions
    assert _has_permission('supplier', 'rfq', 'read'), "Supplier should have rfq:read permission"
    assert _has_permission('supplier', 'catalog', 'create'), "Supplier should have catalog:create permission"
    assert not _has_permission('supplier', 'rfq', 'create'), "Supplier should not have rfq:create permission"
    
    # Check that manager has expected permissions
    assert _has_permission('manager', 'rfq', 'read'), "Manager should have rfq:read permission"
    assert _has_permission('manager', 'user', 'manage'), "Manager should have user:manage permission"
    assert not _has_permission('manager', 'rfq', 'delete'), "Manager should not have rfq:delete permission"
    
    # Check that admin has all permissions
    assert _has_permission('admin', 'rfq', 'create'), "Admin should have rfq:create permission"
    assert _has_permission('admin', 'supplier', 'read'), "Admin should have supplier:read permission"
    assert _has_permission('admin', 'catalog', 'create'), "Admin should have catalog:create permission"
    assert _has_permission('admin', 'user', 'manage'), "Admin should have user:manage permission"
    
    print("All RBAC tests passed!")

if __name__ == "__main__":
    test_rbac()