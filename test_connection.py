from supabase import create_client, Client

# Replace with your own credentials from Supabase Project Settings → API
url = "https://qkobfoeypazszftbnkmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrb2Jmb2V5cGF6c3pmdGJua21iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4Njc1MzAsImV4cCI6MjA3NjQ0MzUzMH0.AdkoAaSAL-RK6kH3fTa7vKf5gLNkS03qqp8XvR97ccE"

try:
    supabase: Client = create_client(url, key)
    print("✅ Supabase client created successfully!")

    # Try reading from a small table to confirm connection
    response = supabase.table("locations").select("*").limit(1).execute()
    print("✅ Connection test successful!")
    print("Sample data:", response.data)

except Exception as e:
    print("❌ Connection failed:")
    print(e)
