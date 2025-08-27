-- Add verified flag to companies
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE;

-- Add 2FA columns to users
ALTER TABLE users
ADD COLUMN IF NOT EXISTS two_factor_secret TEXT,
ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;
