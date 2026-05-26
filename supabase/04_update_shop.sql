
-- Add missing columns to shops table if they don't exist
ALTER TABLE shops ADD COLUMN IF NOT EXISTS mobile TEXT;
ALTER TABLE shops ADD COLUMN IF NOT EXISTS logo_url TEXT;

-- Verify columns
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'shops';
