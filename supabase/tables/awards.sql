CREATE TABLE awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID NOT NULL,
    offer_id UUID,
    selected_by UUID NOT NULL,
    award_amount DECIMAL(15,2),
    award_date TIMESTAMPTZ DEFAULT NOW(),
    contract_terms JSONB,
    status VARCHAR(50) DEFAULT 'awarded',
    notes TEXT
);