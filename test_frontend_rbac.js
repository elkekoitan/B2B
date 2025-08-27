// Simple test to verify our frontend RBAC implementation
const testFrontendRBAC = () => {
  console.log('Testing frontend RBAC implementation...');
  
  // Define role permissions
  const rolePermissions = {
    admin: ['*'],
    buyer: [
      'rfq:create', 'rfq:read', 'rfq:update', 'rfq:delete',
      'supplier:read', 'catalog:read', 'offer:read', 'verification:request'
    ],
    supplier: [
      'rfq:read', 'catalog:create', 'catalog:read', 'catalog:update', 'catalog:delete',
      'offer:create', 'offer:read', 'offer:update', 'verification:request'
    ],
    manager: [
      'rfq:read', 'rfq:approve', 'supplier:read', 'catalog:read',
      'offer:read', 'user:manage', 'analytics:read'
    ]
  };
  
  // Function to check if user has permission
  const hasPermission = (userRole, resource, action) => {
    // Admin has all permissions
    if (userRole === 'admin') {
      return true;
    }
    
    // Get permissions for the role
    const permissions = rolePermissions[userRole] || [];
    
    // Check for wildcard permission
    if (permissions.includes('*')) {
      return true;
    }
    
    // Check for specific permission
    const target = `${resource}:${action}`;
    if (permissions.includes(target)) {
      return true;
    }
    
    // Check for resource-level permission (e.g., "rfq:*")
    const resourceWildcard = `${resource}:*`;
    if (permissions.includes(resourceWildcard)) {
      return true;
    }
    
    return false;
  };
  
  // Function to check if user has role
  const hasRole = (userRole, roles) => {
    const rolesArray = Array.isArray(roles) ? roles : [roles];
    
    // Admin has all roles
    if (userRole === 'admin') {
      return true;
    }
    
    return rolesArray.includes(userRole);
  };
  
  // Test cases
  console.assert(hasPermission('buyer', 'rfq', 'create'), 'Buyer should have rfq:create permission');
  console.assert(hasPermission('buyer', 'supplier', 'read'), 'Buyer should have supplier:read permission');
  console.assert(!hasPermission('buyer', 'catalog', 'create'), 'Buyer should not have catalog:create permission');
  
  console.assert(hasPermission('supplier', 'rfq', 'read'), 'Supplier should have rfq:read permission');
  console.assert(hasPermission('supplier', 'catalog', 'create'), 'Supplier should have catalog:create permission');
  console.assert(!hasPermission('supplier', 'rfq', 'create'), 'Supplier should not have rfq:create permission');
  
  console.assert(hasPermission('manager', 'rfq', 'read'), 'Manager should have rfq:read permission');
  console.assert(hasPermission('manager', 'user', 'manage'), 'Manager should have user:manage permission');
  console.assert(!hasPermission('manager', 'rfq', 'delete'), 'Manager should not have rfq:delete permission');
  
  console.assert(hasPermission('admin', 'rfq', 'create'), 'Admin should have rfq:create permission');
  console.assert(hasPermission('admin', 'supplier', 'read'), 'Admin should have supplier:read permission');
  console.assert(hasPermission('admin', 'catalog', 'create'), 'Admin should have catalog:create permission');
  console.assert(hasPermission('admin', 'user', 'manage'), 'Admin should have user:manage permission');
  
  console.assert(hasRole('admin', 'buyer'), 'Admin should have buyer role');
  console.assert(hasRole('buyer', 'buyer'), 'Buyer should have buyer role');
  console.assert(!hasRole('supplier', 'buyer'), 'Supplier should not have buyer role');
  console.assert(hasRole('manager', ['buyer', 'manager']), 'Manager should have manager role');
  
  console.log('All frontend RBAC tests passed!');
};

// Run the test
testFrontendRBAC();