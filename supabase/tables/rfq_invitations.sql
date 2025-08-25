CREATE TABLE rfq_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID NOT NULL,
    supplier_id UUID NOT NULL,
    invited_by UUID NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ
);