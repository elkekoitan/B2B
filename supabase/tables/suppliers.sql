CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    specializations TEXT[],
    certifications TEXT[],
    rating DECIMAL(3,2) DEFAULT 0,
    total_completed_orders INTEGER DEFAULT 0,
    average_response_time INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT false,
    verification_date TIMESTAMPTZ,
    profile_completion_score INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);