-- Create role management tables for RBAC system

-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create role_assignments table
CREATE TABLE IF NOT EXISTS role_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES user_roles(id),
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

-- Insert default roles
INSERT INTO user_roles (name, description, permissions) VALUES
('admin', 'Administrator with full system access', '["*"]'),
('buyer', 'Buyer role for creating RFQs and managing procurement', '["rfq:create", "rfq:read", "rfq:update", "rfq:delete", "supplier:read", "catalog:read", "offer:read", "verification:request"]'),
('supplier', 'Supplier role for responding to RFQs and managing catalogs', '["rfq:read", "catalog:create", "catalog:read", "catalog:update", "catalog:delete", "offer:create", "offer:read", "offer:update", "verification:request"]'),
('manager', 'Manager role for team and approval management', '["rfq:read", "rfq:approve", "supplier:read", "catalog:read", "offer:read", "user:manage", "analytics:read"]')
ON CONFLICT (name) DO NOTHING;

-- Add role column to users table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='role'
    ) THEN
        ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_roles_name ON user_roles(name);
CREATE INDEX IF NOT EXISTS idx_role_assignments_user_id ON role_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_role_assignments_role_id ON role_assignments(role_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);