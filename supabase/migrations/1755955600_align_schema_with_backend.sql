-- Align suppliers table with backend models
-- Make company_id optional and add missing columns used by API
ALTER TABLE IF EXISTS suppliers
    ALTER COLUMN company_id DROP NOT NULL;

-- Add columns if they do not exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='name'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN name TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='email'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN email TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='phone'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN phone TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='company'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN company TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='address'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN address TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='website'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN website TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='categories'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN categories TEXT[];
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='suppliers' AND column_name='description'
    ) THEN
        ALTER TABLE suppliers ADD COLUMN description TEXT;
    END IF;

    -- Keep existing verified and rating columns; ensure types
    -- created_at/updated_at already exist per initial schema
END $$;

-- Align offers table with backend models
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='offers' AND column_name='unit_price'
    ) THEN
        ALTER TABLE offers ADD COLUMN unit_price DECIMAL(15,2);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='offers' AND column_name='total_price'
    ) THEN
        ALTER TABLE offers ADD COLUMN total_price DECIMAL(15,2);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='offers' AND column_name='terms'
    ) THEN
        ALTER TABLE offers ADD COLUMN terms TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='offers' AND column_name='notes'
    ) THEN
        ALTER TABLE offers ADD COLUMN notes TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='offers' AND column_name='submitted_at'
    ) THEN
        ALTER TABLE offers ADD COLUMN submitted_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

