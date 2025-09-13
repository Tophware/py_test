# Example usage of the create_sector_polygon function

"""
Function signature:
create_sector_polygon(origin_lat, origin_lon, bearing_center, width_degrees, min_radius_miles, max_radius_miles)

Parameters:
- origin_lat, origin_lon: Center point coordinates (degrees)
- bearing_center: Central bearing direction in radians
- width_degrees: Total angular width in degrees (split evenly on both sides)
- min_radius_miles: Inner radius in miles
- max_radius_miles: Outer radius in miles

Returns:
- List of [lat, lon] coordinates forming the sector polygon

Example usage:
"""

import math

# Example 1: Create a 45-degree sector from 5 to 15 miles
# Starting from coordinates 40.0, -74.0, pointing northeast (45 degrees)
bearing_northeast = math.radians(45)  # Convert 45 degrees to radians

sector_coords = create_sector_polygon(
    origin_lat=40.0,
    origin_lon=-74.0,
    bearing_center=bearing_northeast,
    width_degrees=45,  # 45-degree total width (22.5° each side)
    min_radius_miles=5,  # Inner radius 5 miles
    max_radius_miles=15,  # Outer radius 15 miles
)

# Then add to your Folium map:
folium.Polygon(
    locations=sector_coords,
    popup="Search Area (5-15 miles, 45° width)",
    tooltip="Search Sector",
    color="blue",
    weight=2,
    fill=True,
    fillColor="lightblue",
    fillOpacity=0.3,
).add_to(your_map)

# Example 2: Create sector from calculated bearing (like Day 15 New Hope Bridge)
# Calculate bearing from two points first, then use it:
start_lat, start_lon = 40.364551, -74.950404
direction_lat, direction_lon = 40.365207, -74.947155

lat1, lon1 = math.radians(start_lat), math.radians(start_lon)
lat2, lon2 = math.radians(direction_lat), math.radians(direction_lon)
dlon = lon2 - lon1

calculated_bearing = math.atan2(
    math.sin(dlon) * math.cos(lat2),
    math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon),
)

sector_coords = create_sector_polygon(
    origin_lat=start_lat,
    origin_lon=start_lon,
    bearing_center=calculated_bearing,
    width_degrees=30,  # 30-degree width
    min_radius_miles=10,  # 10-mile inner radius
    max_radius_miles=25,  # 25-mile outer radius
)
