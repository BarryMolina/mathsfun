-- Comprehensive seed data for local Supabase development environment
-- This file provides realistic test data for development and testing of the SM-2 spaced repetition system
--
-- Data includes: test users, math fact performances, and attempt histories with realistic SM-2 progression

-- Step 1: Create test users in auth.users first, then user profiles
-- Note: These UUIDs are for local development only and should not be used in production

-- Insert test users into auth.users table first
INSERT INTO auth.users (
    id, email, encrypted_password, email_confirmed_at, created_at, updated_at, 
    last_sign_in_at, raw_app_meta_data, raw_user_meta_data, is_super_admin, role
) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'alice@example.com',
    crypt('testpassword123', gen_salt('bf')),
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day',
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Student Alice"}',
    false,
    'authenticated'
),
(
    '22222222-2222-2222-2222-222222222222',
    'bob@example.com',
    crypt('testpassword123', gen_salt('bf')),
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '2 hours',
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Student Bob"}',
    false,
    'authenticated'
),
(
    '33333333-3333-3333-3333-333333333333',
    'charlie@example.com',
    crypt('testpassword123', gen_salt('bf')),
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days',
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Student Charlie"}',
    false,
    'authenticated'
);

-- Insert corresponding user profiles
INSERT INTO public.user_profiles (id, display_name, email, created_at, last_active) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'Student Alice',
    'alice@example.com',
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day'
),
(
    '22222222-2222-2222-2222-222222222222', 
    'Student Bob',
    'bob@example.com',
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '2 hours'
),
(
    '33333333-3333-3333-3333-333333333333',
    'Student Charlie', 
    'charlie@example.com',
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '3 days'
);

-- Step 2: Create math fact performances with varying SM-2 states
-- Alice: Beginner with mixed performance
INSERT INTO public.math_fact_performances (
    id, user_id, fact_key, total_attempts, correct_attempts, total_response_time_ms,
    fastest_response_ms, slowest_response_ms, last_attempted, created_at, updated_at,
    repetition_number, easiness_factor, interval_days, next_review_date, last_sm2_grade
) VALUES
-- Alice's facts - mixed performance, some struggling
('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', '7+8', 5, 3, 9500, 1800, 4200, NOW() - INTERVAL '2 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '2 days', 1, 2.30, 6, NOW() + INTERVAL '4 days', 4),
('a2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', '6+7', 8, 5, 15000, 2100, 3800, NOW() - INTERVAL '1 day', NOW() - INTERVAL '12 days', NOW() - INTERVAL '1 day', 2, 2.40, 8, NOW() + INTERVAL '7 days', 3),
('a3333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', '9+4', 3, 1, 2500, 2500, 2500, NOW() - INTERVAL '5 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '5 days', 0, 1.80, 1, NOW() - INTERVAL '4 days', 1),
('a4444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '5+6', 4, 4, 7200, 1500, 2400, NOW() - INTERVAL '3 days', NOW() - INTERVAL '6 days', NOW() - INTERVAL '3 days', 2, 2.60, 10, NOW() + INTERVAL '7 days', 5),
('a5555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', '8+9', 2, 1, 3200, 3200, 3200, NOW() - INTERVAL '1 day', NOW() - INTERVAL '4 days', NOW() - INTERVAL '1 day', 0, 2.20, 1, NOW() - INTERVAL '1 hour', 2),

-- Bob's facts - advanced student with good performance
('b1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '7+8', 6, 6, 9600, 1200, 2000, NOW() - INTERVAL '3 days', NOW() - INTERVAL '15 days', NOW() - INTERVAL '3 days', 3, 2.90, 18, NOW() + INTERVAL '15 days', 5),
('b2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', '6+7', 4, 4, 5600, 1100, 1800, NOW() - INTERVAL '1 day', NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 day', 2, 2.70, 12, NOW() + INTERVAL '11 days', 4),
('b3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', '9+6', 5, 5, 7000, 1000, 1800, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '8 days', NOW() - INTERVAL '2 hours', 3, 3.10, 25, NOW() + INTERVAL '23 days', 5),
('b4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', '8+8', 3, 3, 3900, 1200, 1500, NOW() - INTERVAL '4 days', NOW() - INTERVAL '7 days', NOW() - INTERVAL '4 days', 1, 2.50, 6, NOW() + INTERVAL '2 days', 4),
('b5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', '4+9', 7, 6, 10500, 1300, 2200, NOW() - INTERVAL '6 hours', NOW() - INTERVAL '12 days', NOW() - INTERVAL '6 hours', 2, 2.80, 15, NOW() + INTERVAL '9 days', 4),

-- Charlie's facts - struggling student with poor performance
('c1111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', '7+8', 12, 4, 16000, 2800, 6500, NOW() - INTERVAL '1 day', NOW() - INTERVAL '14 days', NOW() - INTERVAL '1 day', 0, 1.30, 1, NOW() - INTERVAL '2 hours', 0),
('c2222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '6+7', 9, 3, 15000, 3500, 7200, NOW() - INTERVAL '4 days', NOW() - INTERVAL '16 days', NOW() - INTERVAL '4 days', 0, 1.50, 1, NOW() - INTERVAL '3 days', 1),
('c3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', '3+4', 6, 5, 11000, 1900, 3200, NOW() - INTERVAL '2 days', NOW() - INTERVAL '9 days', NOW() - INTERVAL '2 days', 1, 2.10, 3, NOW() + INTERVAL '1 day', 3),
('c4444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', '5+5', 8, 6, 15600, 2200, 3400, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '11 days', NOW() - INTERVAL '5 hours', 1, 2.30, 4, NOW() + INTERVAL '1 day', 4),
('c5555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', '2+3', 4, 4, 6800, 1400, 2100, NOW() - INTERVAL '3 days', NOW() - INTERVAL '7 days', NOW() - INTERVAL '3 days', 2, 2.60, 8, NOW() + INTERVAL '5 days', 4);

-- Step 3: Create realistic math fact attempts showing learning progression
-- Alice's attempts for 7+8 (struggling then improving)
INSERT INTO public.math_fact_attempts (
    id, user_id, fact_key, operand1, operand2, user_answer, correct_answer,
    is_correct, response_time_ms, incorrect_attempts_in_session, sm2_grade, attempted_at
) VALUES
('aa111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', '7+8', 7, 8, NULL, 15, false, 8000, 3, 0, NOW() - INTERVAL '10 days'),
('aa222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', '7+8', 7, 8, 15, 15, true, 4200, 1, 2, NOW() - INTERVAL '8 days'),
('aa333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', '7+8', 7, 8, 15, 15, true, 3200, 0, 3, NOW() - INTERVAL '5 days'),
('aa444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '7+8', 7, 8, 15, 15, true, 2800, 0, 3, NOW() - INTERVAL '3 days'),
('aa555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', '7+8', 7, 8, 15, 15, true, 1800, 0, 4, NOW() - INTERVAL '2 days'),

-- Bob's attempts for 7+8 (consistently good performance)
('bb111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 2000, 0, 4, NOW() - INTERVAL '15 days'),
('bb222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 1800, 0, 4, NOW() - INTERVAL '12 days'),
('bb333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 1600, 0, 5, NOW() - INTERVAL '8 days'),
('bb444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 1400, 0, 5, NOW() - INTERVAL '5 days'),
('bb555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 1200, 0, 5, NOW() - INTERVAL '3 days'),
('bb666666-6666-6666-6666-666666666666', '22222222-2222-2222-2222-222222222222', '7+8', 7, 8, 15, 15, true, 1300, 0, 5, NOW() - INTERVAL '1 day'),

-- Charlie's attempts for 7+8 (poor performance, frequent errors)
('cc111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, 14, 15, false, 6500, 2, 0, NOW() - INTERVAL '14 days'),
('cc222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, NULL, 15, false, 8200, 4, 0, NOW() - INTERVAL '12 days'),
('cc333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, 15, 15, true, 5800, 1, 1, NOW() - INTERVAL '10 days'),
('cc444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, 16, 15, false, 4200, 1, 1, NOW() - INTERVAL '8 days'),
('cc555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, 15, 15, true, 4500, 0, 3, NOW() - INTERVAL '6 days'),
('cc666666-6666-6666-6666-666666666666', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, NULL, 15, false, 7800, 3, 0, NOW() - INTERVAL '4 days'),
('cc777777-7777-7777-7777-777777777777', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, 15, 15, true, 3800, 0, 3, NOW() - INTERVAL '2 days'),
('cc888888-8888-8888-8888-888888888888', '33333333-3333-3333-3333-333333333333', '7+8', 7, 8, NULL, 15, false, 6200, 2, 0, NOW() - INTERVAL '1 day'),

-- Additional attempts for other facts (samples)
-- Alice's 6+7 attempts
('aa666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', '6+7', 6, 7, 13, 13, true, 3800, 0, 3, NOW() - INTERVAL '12 days'),
('aa777777-7777-7777-7777-777777777777', '11111111-1111-1111-1111-111111111111', '6+7', 6, 7, 13, 13, true, 2900, 0, 3, NOW() - INTERVAL '8 days'),
('aa888888-8888-8888-8888-888888888888', '11111111-1111-1111-1111-111111111111', '6+7', 6, 7, 13, 13, true, 2100, 0, 4, NOW() - INTERVAL '1 day'),

-- Bob's 9+6 attempts (excellent progression)
('bb777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222222', '9+6', 9, 6, 15, 15, true, 1800, 0, 4, NOW() - INTERVAL '8 days'),
('bb888888-8888-8888-8888-888888888888', '22222222-2222-2222-2222-222222222222', '9+6', 9, 6, 15, 15, true, 1200, 0, 5, NOW() - INTERVAL '4 days'),
('bb999999-9999-9999-9999-999999999999', '22222222-2222-2222-2222-222222222222', '9+6', 9, 6, 15, 15, true, 1000, 0, 5, NOW() - INTERVAL '2 hours'),

-- Charlie's 3+4 attempts (gradual improvement)
('cc999999-9999-9999-9999-999999999999', '33333333-3333-3333-3333-333333333333', '3+4', 3, 4, 7, 7, true, 3200, 0, 3, NOW() - INTERVAL '9 days'),
('cc000000-0000-0000-0000-000000000000', '33333333-3333-3333-3333-333333333333', '3+4', 3, 4, 7, 7, true, 2400, 0, 4, NOW() - INTERVAL '5 days'),
('cc111110-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', '3+4', 3, 4, 7, 7, true, 1900, 0, 4, NOW() - INTERVAL '2 days');

-- Success message to confirm seed file ran
SELECT 'Comprehensive math facts seed data loaded successfully!' as message,
       COUNT(DISTINCT user_id) as users_created,
       COUNT(*) as performances_created
FROM public.math_fact_performances;

SELECT 'Math fact attempts created:' as message,
       COUNT(*) as attempts_created,
       COUNT(DISTINCT fact_key) as unique_facts
FROM public.math_fact_attempts;