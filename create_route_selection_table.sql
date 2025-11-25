-- Create route_selections table for dashboard-Python communication
CREATE TABLE IF NOT EXISTS route_selections (
    id INTEGER PRIMARY KEY DEFAULT 1,
    selected_route_id INTEGER,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Insert initial record
INSERT INTO route_selections (id, selected_route_id, timestamp) 
VALUES (1, NULL, now()) 
ON CONFLICT (id) DO UPDATE SET 
  selected_route_id = NULL,
  timestamp = now();