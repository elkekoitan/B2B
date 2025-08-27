# Simple test to verify our RBAC implementation without Supabase dependencies
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath('.'))

# Mock the Supabase client to avoid configuration issues
class MockSupabaseClient:
    def table(self, table_name):
        return MockSupabaseTable(table_name)

class MockSupabaseTable:
    def __init__(self, table_name):
        self.table_name = table_name
    
    def select(self, *args, **kwargs):
        return self
    
    def eq(self, *args, **kwargs):
        return self
    
    def maybe_single(self):
        return self
    
    def execute(self):
        # Return mock data for users table
        if self.table_name == "users":
            return MockResponse([{
                "id": "test-user-id",
                "email": "test@example.com",
                "role": "admin"
            }])
        return MockResponse([])

class MockResponse:
    def __init__(self, data):
        self.data = data

# Patch the Supabase client
import app.database
app.database.supabase_client = MockSupabaseClient()
app.database.supabase = app.database.supabase_client
app.database.supabase_admin = app.database.supabase_client

# Test the role permissions
def test_rbac():
    print("Testing RBAC implementation...")
    
    # Test the role permissions
    from app.auth import ROLE_PERMISSIONS
    
    # Check that we have the expected roles
    expected_roles = ['admin', 'buyer', 'supplier', 'manager']
    for role in expected_roles:
        assert role in ROLE_PERMISSIONS, f"Role {role} not found in ROLE_PERMISSIONS"
    
    # Check that admin has all permissions
    assert "*" in ROLE_PERMISSIONS['admin'], "Admin should have all permissions"
    
    # Check that buyer has expected permissions
    buyer_permissions = ROLE_PERMISSIONS['buyer']
    assert 'rfq:create' in buyer_permissions, "Buyer should have rfq:create permission"
    assert 'supplier:read' in buyer_permissions, "Buyer should have supplier:read permission"
    
    # Check that supplier has expected permissions
    supplier_permissions = ROLE_PERMISSIONS['supplier']
    assert 'rfq:read' in supplier_permissions, "Supplier should have rfq:read permission"
    assert 'catalog:create' in supplier_permissions, "Supplier should have catalog:create permission"
    
    # Check that manager has expected permissions
    manager_permissions = ROLE_PERMISSIONS['manager']
    assert 'rfq:read' in manager_permissions, "Manager should have rfq:read permission"
    assert 'user:manage' in manager_permissions, "Manager should have user:manage permission"
    
    print("All RBAC tests passed!")

if __name__ == "__main__":
    test_rbac()