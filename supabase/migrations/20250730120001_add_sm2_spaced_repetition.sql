-- Add SM-2 Spaced Repetition Algorithm Support
-- This migration transforms the existing mastery system to use SM-2 algorithm

-- Step 1: Rename addition_fact_performances to math_fact_performances for extensibility
ALTER TABLE addition_fact_performances RENAME TO math_fact_performances;

-- Step 2: Remove mastery level constraint and column
ALTER TABLE math_fact_performances DROP CONSTRAINT valid_mastery_level;
ALTER TABLE math_fact_performances DROP COLUMN mastery_level;

-- Step 3: Add SM-2 algorithm columns
ALTER TABLE math_fact_performances 
ADD COLUMN repetition_number INTEGER NOT NULL DEFAULT 0,
ADD COLUMN easiness_factor DECIMAL(3,2) NOT NULL DEFAULT 2.50,
ADD COLUMN interval_days INTEGER NOT NULL DEFAULT 1,
ADD COLUMN next_review_date TIMESTAMP WITH TIME ZONE;

-- Step 4: Create math_fact_attempts table for time series data
CREATE TABLE public.math_fact_attempts (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    fact_key TEXT NOT NULL,
    operand1 INTEGER NOT NULL,
    operand2 INTEGER NOT NULL,
    user_answer INTEGER,
    correct_answer INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    response_time_ms INTEGER NOT NULL,
    incorrect_attempts_in_session INTEGER NOT NULL DEFAULT 0,
    sm2_grade INTEGER,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 5: Add constraints for SM-2 data integrity
ALTER TABLE math_fact_performances 
ADD CONSTRAINT math_fact_performances_easiness_factor_range 
CHECK (easiness_factor >= 1.30 AND easiness_factor <= 4.00);

ALTER TABLE math_fact_performances 
ADD CONSTRAINT math_fact_performances_repetition_number_non_negative 
CHECK (repetition_number >= 0);

ALTER TABLE math_fact_performances 
ADD CONSTRAINT math_fact_performances_interval_days_positive 
CHECK (interval_days > 0);

ALTER TABLE math_fact_attempts 
ADD CONSTRAINT math_fact_attempts_sm2_grade_range 
CHECK (sm2_grade >= 0 AND sm2_grade <= 5);

ALTER TABLE math_fact_attempts 
ADD CONSTRAINT math_fact_attempts_incorrect_attempts_non_negative 
CHECK (incorrect_attempts_in_session >= 0);

-- Step 6: Create primary key and indexes for math_fact_attempts
CREATE UNIQUE INDEX math_fact_attempts_pkey ON public.math_fact_attempts USING btree (id);
ALTER TABLE math_fact_attempts ADD CONSTRAINT math_fact_attempts_pkey PRIMARY KEY using index math_fact_attempts_pkey;

-- Step 7: Create performance indexes for SM-2 queries
CREATE INDEX idx_math_fact_performances_review_due 
ON public.math_fact_performances USING btree (user_id, next_review_date, fact_key);

CREATE INDEX idx_math_fact_attempts_user_fact 
ON public.math_fact_attempts USING btree (user_id, fact_key);

CREATE INDEX idx_math_fact_attempts_user_time 
ON public.math_fact_attempts USING btree (user_id, attempted_at DESC);

CREATE INDEX idx_math_fact_attempts_attempted_at 
ON public.math_fact_attempts USING btree (attempted_at DESC);

-- Step 8: Update constraints and indexes to match new table name
-- First drop constraints that depend on indexes
ALTER TABLE math_fact_performances DROP CONSTRAINT addition_fact_performances_pkey;
ALTER TABLE math_fact_performances DROP CONSTRAINT addition_fact_performances_user_fact_unique;

-- Drop the old indexes
DROP INDEX IF EXISTS idx_addition_fact_performances_mastery;
DROP INDEX IF EXISTS addition_fact_performances_user_fact_unique;
DROP INDEX IF EXISTS addition_fact_performances_pkey;

-- Recreate indexes with new names
CREATE UNIQUE INDEX math_fact_performances_pkey ON public.math_fact_performances USING btree (id);
CREATE UNIQUE INDEX math_fact_performances_user_fact_unique ON public.math_fact_performances USING btree (user_id, fact_key);

-- Add constraints using the new indexes
ALTER TABLE math_fact_performances ADD CONSTRAINT math_fact_performances_pkey PRIMARY KEY using index math_fact_performances_pkey;
ALTER TABLE math_fact_performances ADD CONSTRAINT math_fact_performances_user_fact_unique UNIQUE using index math_fact_performances_user_fact_unique;

-- Step 9: Add foreign key constraint for math_fact_attempts
ALTER TABLE math_fact_attempts 
ADD CONSTRAINT math_fact_attempts_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE;

-- Step 10: Enable row level security for math_fact_attempts
ALTER TABLE math_fact_attempts ENABLE ROW LEVEL SECURITY;

-- Step 11: Grant permissions for math_fact_attempts (all roles)
GRANT DELETE ON TABLE math_fact_attempts TO anon;
GRANT INSERT ON TABLE math_fact_attempts TO anon;
GRANT REFERENCES ON TABLE math_fact_attempts TO anon;
GRANT SELECT ON TABLE math_fact_attempts TO anon;
GRANT TRIGGER ON TABLE math_fact_attempts TO anon;
GRANT TRUNCATE ON TABLE math_fact_attempts TO anon;
GRANT UPDATE ON TABLE math_fact_attempts TO anon;

GRANT DELETE ON TABLE math_fact_attempts TO authenticated;
GRANT INSERT ON TABLE math_fact_attempts TO authenticated;
GRANT REFERENCES ON TABLE math_fact_attempts TO authenticated;
GRANT SELECT ON TABLE math_fact_attempts TO authenticated;
GRANT TRIGGER ON TABLE math_fact_attempts TO authenticated;
GRANT TRUNCATE ON TABLE math_fact_attempts TO authenticated;
GRANT UPDATE ON TABLE math_fact_attempts TO authenticated;

GRANT DELETE ON TABLE math_fact_attempts TO service_role;
GRANT INSERT ON TABLE math_fact_attempts TO service_role;
GRANT REFERENCES ON TABLE math_fact_attempts TO service_role;
GRANT SELECT ON TABLE math_fact_attempts TO service_role;
GRANT TRIGGER ON TABLE math_fact_attempts TO service_role;
GRANT TRUNCATE ON TABLE math_fact_attempts TO service_role;
GRANT UPDATE ON TABLE math_fact_attempts TO service_role;

-- Step 12: Create RLS policies for math_fact_attempts
CREATE POLICY "Users can view own math fact attempts"
ON math_fact_attempts
AS PERMISSIVE
FOR SELECT
TO PUBLIC
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own math fact attempts"
ON math_fact_attempts
AS PERMISSIVE
FOR INSERT
TO PUBLIC
WITH CHECK (auth.uid() = user_id);

-- Step 13: Update existing RLS policies to reference new table name
DROP POLICY IF EXISTS "Users can insert own fact performances" ON math_fact_performances;
DROP POLICY IF EXISTS "Users can update own fact performances" ON math_fact_performances;
DROP POLICY IF EXISTS "Users can view own fact performances" ON math_fact_performances;

CREATE POLICY "Users can view own math fact performances"
ON math_fact_performances
AS PERMISSIVE
FOR SELECT
TO PUBLIC
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own math fact performances"
ON math_fact_performances
AS PERMISSIVE
FOR INSERT
TO PUBLIC
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own math fact performances"
ON math_fact_performances
AS PERMISSIVE
FOR UPDATE
TO PUBLIC
USING (auth.uid() = user_id);

-- Step 14: Update trigger name
DROP TRIGGER IF EXISTS update_addition_fact_performances_updated_at ON math_fact_performances;
CREATE TRIGGER update_math_fact_performances_updated_at 
BEFORE UPDATE ON math_fact_performances 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 15: Initialize existing records with SM-2 defaults and set initial review dates
UPDATE math_fact_performances 
SET next_review_date = COALESCE(last_attempted, created_at) + INTERVAL '1 day'
WHERE next_review_date IS NULL;