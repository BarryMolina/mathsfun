-- Add last_sm2_grade column to math_fact_performances table
-- This stores the most recent SM2 grade for quick access without requiring joins

-- Step 1: Add the new column
ALTER TABLE math_fact_performances 
ADD COLUMN last_sm2_grade INTEGER;

-- Step 2: Add constraint to validate SM2 grade range (0-5)
ALTER TABLE math_fact_performances 
ADD CONSTRAINT math_fact_performances_last_sm2_grade_range 
CHECK (last_sm2_grade IS NULL OR (last_sm2_grade >= 0 AND last_sm2_grade <= 5));

-- Step 3: Populate existing records with their most recent SM2 grade
-- This subquery finds the most recent attempt for each fact and gets its SM2 grade
UPDATE math_fact_performances 
SET last_sm2_grade = (
    SELECT sm2_grade 
    FROM math_fact_attempts 
    WHERE math_fact_attempts.user_id = math_fact_performances.user_id 
    AND math_fact_attempts.fact_key = math_fact_performances.fact_key 
    AND sm2_grade IS NOT NULL
    ORDER BY attempted_at DESC 
    LIMIT 1
)
WHERE EXISTS (
    SELECT 1 
    FROM math_fact_attempts 
    WHERE math_fact_attempts.user_id = math_fact_performances.user_id 
    AND math_fact_attempts.fact_key = math_fact_performances.fact_key 
    AND sm2_grade IS NOT NULL
);

-- Step 4: Create index for performance if needed for queries filtering by SM2 grade
CREATE INDEX IF NOT EXISTS idx_math_fact_performances_last_sm2_grade 
ON math_fact_performances (user_id, last_sm2_grade) 
WHERE last_sm2_grade IS NOT NULL;