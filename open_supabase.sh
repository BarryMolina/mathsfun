#!/bin/bash

# Get Supabase URL from environment or construct from project_id
if [ -n "$SUPABASE_URL" ]; then
    URL="$SUPABASE_URL"
else
    PROJECT_ID=$(grep "project_id = " supabase/config.toml | sed 's/.*project_id = "\([^"]*\)".*/\1/')
    URL="https://$PROJECT_ID.supabase.co"
fi

# Convert to dashboard URL and open
PROJECT_REF=$(echo "$URL" | sed 's|https://||' | sed 's|\.supabase\.co||')
open "https://supabase.com/dashboard/project/$PROJECT_REF" 