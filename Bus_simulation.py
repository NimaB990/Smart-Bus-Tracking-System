from supabase import create_client, Client
import time
from datetime import datetime

# --- Supabase credentials ---
url = "https://qkobfoeypazszftbnkmb.supabase.co" 
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrb2Jmb2V5cGF6c3pmdGJua21iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4Njc1MzAsImV4cCI6MjA3NjQ0MzUzMH0.AdkoAaSAL-RK6kH3fTa7vKf5gLNkS03qqp8XvR97ccE"

# --- Create client ---
supabase: Client = create_client(url, key)

# --- Example route coordinates (Kandy to Colombo) ---
route = [
    (7.2906, 80.6337),
    (7.2915, 80.6350),
    (7.2925, 80.6362),
    (7.2938, 80.6378),
    (7.2950, 80.6390),
]

# --- Simulate bus data ---
bus_id = 1  # must match an existing bus in your 'buses' table
speed = 40  # km/h

while True:
    for lat, lng in route:
        data = {
            "bus_id": bus_id,
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Insert data into Supabase 'locations' table
        supabase.table("locations").insert(data).execute()

        print(f"📍 Updated bus {bus_id} location: {lat}, {lng}")
        time.sleep(3)  # wait 3 seconds before next update
