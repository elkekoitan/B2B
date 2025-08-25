CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID NOT NULL,
    supplier_id UUID NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    delivery_time INTEGER,
    delivery_terms TEXT,
    warranty_terms TEXT,
    payment_terms TEXT,
    technical_specs JSONB,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'submitted',
    valid_until DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);