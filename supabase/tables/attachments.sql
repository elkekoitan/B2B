CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID,
    offer_id UUID,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);