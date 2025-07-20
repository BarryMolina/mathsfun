import dotenv
import os

dotenv.load_dotenv()

url = os.getenv("SUPABASE_URL") or ""
key = os.getenv("SUPABASE_KEY") or ""

print(url, key)

from supabase import create_client, Client

supabase: Client = create_client(url, key)

res = supabase.auth.sign_in_with_oauth(
    {
        "provider": "google",
    }
)

print(res)

# print(supabase.table("users").select("*").execute())
