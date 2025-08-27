-- Jobs table for orchestrated agent workflows
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    company_id UUID,
    rfq_id UUID,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_rfq ON jobs(rfq_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
