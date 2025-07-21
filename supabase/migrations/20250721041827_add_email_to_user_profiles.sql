-- Add email column to user_profiles table
ALTER TABLE public.user_profiles 
ADD COLUMN email TEXT NOT NULL DEFAULT '';

-- Backfill existing users with email from auth.users
UPDATE public.user_profiles 
SET email = (
    SELECT auth.users.email 
    FROM auth.users 
    WHERE auth.users.id = user_profiles.id
)
WHERE user_profiles.email = '';

-- Add unique constraint on email (optional but recommended)
ALTER TABLE public.user_profiles 
ADD CONSTRAINT user_profiles_email_unique UNIQUE (email);

-- Add constraint to ensure email is not empty
ALTER TABLE public.user_profiles 
ADD CONSTRAINT user_profiles_email_not_empty CHECK (char_length(email) > 0);