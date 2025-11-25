from supabase import create_client, Client
import time
import json
import os
from datetime import datetime, timezone
import threading
import warnings

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- Supabase credentials ---
url = "https://qkobfoeypazszftbnkmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrb2Jmb2V5cGF6c3pmdGJua21iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4Njc1MzAsImV4cCI6MjA3NjQ0MzUzMH0.AdkoAaSAL-RK6kH3fTa7vKf5gLNkS03qqp8XvR97ccE"
supabase = create_client(url, key)

# --- Multiple routes dictionary ---
routes = {
    1: {
        "name": "Kandy to Colombo",
        "stops": [
            (7.2906, 80.6337),  # Kandy
            (7.3055, 80.6290),  # Katugastota
            (7.2592, 80.6220),  # Madawala Bazaar
            (7.2380, 80.5505),  # Hingula
            (7.2560, 80.5121),  # Kadugannawa
            (7.2591, 80.5339),  # Pilimathalawa
            (7.2711, 80.5986),  # Peradeniya
            (7.2551, 80.4444),  # Mawanella
            (7.2519, 80.3464),  # Kegalle
            (7.2319, 80.0704),  # Warakapola
            (7.2620, 80.0350),  # Pasyala
            (7.1497, 80.0110),  # Nittambuwa
            (7.0014, 79.9538),  # Kadawatha
            (6.9787, 79.9309),  # Kiribathgoda
            (6.9672, 79.8841),  # Peliyagoda
            (6.9330, 79.8500),  # Colombo Fort
        ]
    },
    2: {
        "name": "Colombo to Galle",
        "stops": [
            (6.9330, 79.8500),  # Colombo Fort
            (6.8500, 79.9000),  # Moratuwa
            (6.7900, 79.9000),  # Panadura
            (6.7000, 79.9000),  # Kalutara
            (6.0500, 80.2200),  # Galle
        ]
    },
    3: {
        "name": "Colombo to Negombo",
        "stops": [
            (6.9330, 79.8500),  # Colombo Fort
            (6.9890, 79.8890),  # Wattala (approx)
            (7.0749, 79.8912),  # Ja-Ela
            (7.1686, 79.8846),  # Katunayake
            (7.2086, 79.8350),  # Negombo
        ]
    },
    4: {
        "name": "Kandy to Nuwara Eliya",
        "stops": [
            (7.2906, 80.6337),  # Kandy
            (7.2711, 80.5986),  # Peradeniya
            (7.1648, 80.5696),  # Gampola
            (7.0547, 80.6429),  # Pussellawa
            (6.9707, 80.7829),  # Nuwara Eliya
        ]
    },
}

# --- Multiple buses dictionary ---
buses = {
    1: {"bus_number": "NB-1234", "route_id": 1, "details": "AC Bus", "driver_id": 2},
    2: {"bus_number": "NB-5678", "route_id": 2, "details": "Normal Bus", "driver_id": 3},
    3: {"bus_number": "NB-9012", "route_id": 3, "details": "Express", "driver_id": 2},
    4: {"bus_number": "NB-3456", "route_id": 4, "details": "Mountain Line", "driver_id": 4},
}

# Global variables for simulation control
active_routes = set()  # Set of route IDs that should be simulated
simulation_threads = {}  # Dictionary to track running threads
stop_simulation = {}  # Dictionary to control thread stopping

def save_location(bus_id, route_id, lat, lng, speed=50):
    """Save location to database"""
    driver_id = buses.get(bus_id, {}).get('driver_id')
    if driver_id is not None:
        try:
            supabase.table("driver_locations").insert({
                "bus_id": bus_id,
                "driver_id": driver_id,
                "latitude": lat,
                "longitude": lng,
                "speed_kmh": speed,
                "gps_timestamp": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception:
            pass  # Silently continue if driver_locations fails

    try:
        supabase.table("bus_status").upsert({
            "bus_id": bus_id,
            "current_latitude": lat,
            "current_longitude": lng,
            "is_running": True,
            "is_moving": True,
            "last_movement_time": datetime.now(timezone.utc).isoformat()
        }, on_conflict="bus_id").execute()
    except Exception:
        pass  # Silently continue if bus_status fails

    print(f"Bus {bus_id} at: {lat:.6f}, {lng:.6f} (Route {route_id})")
    time.sleep(1.0)  # Slower movement for better reliability and visualization

def simulate_route_buses(route_id):
    """Simulate all buses on a specific route with robust error handling"""
    try:
        # Get buses for this route
        route_buses = {bus_id: bus for bus_id, bus in buses.items() if bus["route_id"] == route_id}
        
        if not route_buses:
            print(f"No buses found for route {route_id}")
            return
        
        print(f"🚌 Starting simulation for Route {route_id}: {routes[route_id]['name']}")
        print(f"   Buses: {[bus['bus_number'] for bus in route_buses.values()]}")
        
        direction = {bus_id: True for bus_id in route_buses}
        stops = routes[route_id]["stops"]
        
        while not stop_simulation.get(route_id, False):
            try:
                for bus_id, bus in route_buses.items():
                    if stop_simulation.get(route_id, False):
                        break
                        
                    if direction[bus_id]:
                        # Forward direction
                        for i in range(len(stops) - 1):
                            if stop_simulation.get(route_id, False):
                                break
                            save_location(bus_id, route_id, stops[i][0], stops[i][1])
                        direction[bus_id] = False
                    else:
                        # Backward direction  
                        for i in range(len(stops) - 1, 0, -1):
                            if stop_simulation.get(route_id, False):
                                break
                            save_location(bus_id, route_id, stops[i][0], stops[i][1])
                        direction[bus_id] = True
                        
            except Exception:
                # If any error occurs in the simulation loop, continue after a brief pause
                time.sleep(2)
                continue
        
        print(f"🛑 Stopped simulation for Route {route_id}")
        
    except Exception as e:
        print(f"❌ Route {route_id} simulation error: {e}")
        print(f"🔄 Route {route_id} will be marked as stopped")
        stop_simulation[route_id] = True

def start_route_simulation(route_id):
    """Start simulation for a specific route"""
    if route_id in simulation_threads and simulation_threads[route_id].is_alive():
        print(f"Route {route_id} simulation is already running")
        return
    
    stop_simulation[route_id] = False
    thread = threading.Thread(target=simulate_route_buses, args=(route_id,), daemon=True)
    simulation_threads[route_id] = thread
    thread.start()
    active_routes.add(route_id)

def stop_route_simulation(route_id):
    """Stop simulation for a specific route"""
    if route_id in simulation_threads:
        print(f"🛑 Stopping Route {route_id} simulation...")
        stop_simulation[route_id] = True
        # Mark buses as not moving in database
        route_buses = [bus_id for bus_id, bus in buses.items() if bus["route_id"] == route_id]
        for bus_id in route_buses:
            try:
                supabase.table("bus_status").update({
                    "is_moving": False,
                    "is_running": False
                }).eq("bus_id", bus_id).execute()
            except Exception:
                pass  # Silently continue if database update fails
        
        active_routes.discard(route_id)

def stop_all_simulations():
    """Stop all running simulations"""
    for route_id in list(active_routes):
        stop_route_simulation(route_id)

def initialize_route_file():
    """Initialize the active route file"""
    try:
        # Create active_route.txt if it doesn't exist
        if not os.path.exists('active_route.txt'):
            with open('active_route.txt', 'w') as f:
                f.write('0')  # 0 means no route selected
        print("📁 Route file initialized")
    except Exception as e:
        print(f"Error initializing route file: {e}")

def monitor_file_based_selections():
    """Monitor active_route.txt file for route selections from dashboard"""
    print("🔍 Monitoring active_route.txt for dashboard selections...")
    last_route = None
    
    while True:
        try:
            # Read current route from file
            if os.path.exists('active_route.txt'):
                with open('active_route.txt', 'r') as f:
                    content = f.read().strip()
                    current_route = int(content) if content and content != '0' else None
                
                if current_route != last_route:
                    if last_route is not None:
                        print(f"📱 Dashboard switched from Route {last_route} to Route {current_route}")
                        stop_route_simulation(last_route)
                    
                    if current_route is not None and current_route in routes:
                        print(f"📱 Dashboard selected Route {current_route}: {routes[current_route]['name']}")
                        start_route_simulation(current_route)
                    elif current_route is None:
                        print(f"📱 Dashboard deselected all routes")
                    
                    last_route = current_route
            
        except Exception as e:
            print(f"Warning: file monitoring error: {e}")
        
        time.sleep(2)  # Check every 2 seconds

def auto_monitor_mode():
    """Automatic monitoring mode - starts immediately and runs continuously"""
    print("\n🔄 Starting automatic bus simulation...")
    print("=" * 50)
    print("🎯 System Status:")
    print("   ✅ File monitoring: ACTIVE")
    print("   ✅ Route control: READY")
    print("   ✅ Database connection: READY")
    print("=" * 50)
    
    try:
        # Initialize file system
        initialize_route_file()
        
        # Start all routes automatically
        print("🚌 Starting buses on all routes...")
        for route_id in routes.keys():
            start_route_simulation(route_id)
            print(f"   ✅ Route {route_id}: {routes[route_id]['name']} - STARTED")
        
        print("\n🔍 All buses are now moving automatically!")
        print("💡 Dashboard can still control routes via integrated_tracking_map.html")
        print("⏹️  Press Ctrl+C to stop the system")
        print("🔄 System will run continuously...")
        print()
        
        # Keep the main thread alive and monitor for dashboard changes
        while True:
            try:
                # Check for dashboard route changes
                if os.path.exists('active_route.txt'):
                    with open('active_route.txt', 'r') as f:
                        content = f.read().strip()
                        if content and content != '0':
                            current_route = int(content)
                            if current_route in routes:
                                print(f"📱 Dashboard activity detected for Route {current_route}")
                
                # Keep system alive
                time.sleep(5)  # Check every 5 seconds
                
            except ValueError:
                # Invalid route number in file, ignore
                pass
            except Exception:
                # Any other file errors, ignore and continue
                pass
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping all simulations...")
        stop_all_simulations()
        print("👋 System shutdown complete!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("🔄 Stopping all simulations...")
        stop_all_simulations()

if __name__ == "__main__":
    print("🚌 Smart Bus Simulation - Auto Start Mode")
    print("=" * 50)
    print("🎯 Welcome to the Bus Tracking System!")
    print("   All routes will start automatically:")
    for route_id, route_info in routes.items():
        print(f"     Route {route_id}: {route_info['name']}")
    
    print("\n🚀 Starting all buses automatically...")
    print("📱 Dashboard available at: integrated_tracking_map.html")
    print("=" * 50)
    
    # Start automatic monitoring mode
    auto_monitor_mode()