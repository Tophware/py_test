# Updated Example usage of the create_sector_polygon function

"""
UPDATED Function signature:
create_sector_polygon(center_lat, center_lon, bearing_lat, bearing_lon, width_degrees, min_radius_miles, max_radius_miles)

Parameters:
- center_lat, center_lon: Center point coordinates (where circles are drawn)
- bearing_lat, bearing_lon: Second point to determine direction of center line
- width_degrees: Total angular width in degrees (split evenly on both sides)
- min_radius_miles: Inner radius in miles
- max_radius_miles: Outer radius in miles

Returns:
- List of [lat, lon] coordinates forming the sector polygon

NEW USAGE - Much easier! Just provide two coordinate points:
"""

# Example 1: Create a sector from center point toward a direction point
center_lat, center_lon = 40.0, -74.0  # Where circles are centered
bearing_lat, bearing_lon = 40.1, -73.9  # Point that determines direction

sector_coords = create_sector_polygon(
    center_lat=center_lat,
    center_lon=center_lon,
    bearing_lat=bearing_lat,  # Direction determined by this point
    bearing_lon=bearing_lon,
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

# Example 2: Day 15 New Hope Bridge (matches your current implementation)
center_lat, center_lon = 40.364551, -74.950404  # New Hope Bridge center
bearing_lat, bearing_lon = 40.365207, -74.947155  # Direction point

sector_coords = create_sector_polygon(
    center_lat=center_lat,
    center_lon=center_lon,
    bearing_lat=bearing_lat,  # Function calculates bearing automatically
    bearing_lon=bearing_lon,
    width_degrees=30,  # 30-degree width
    min_radius_miles=10,  # 10-mile inner radius
    max_radius_miles=25,  # 25-mile outer radius
)

# MUCH SIMPLER than calculating bearings manually!
# No more math.radians() or atan2() calculations needed!

# Example 3: For your future requests, you just need:
# "Center coordinates: X, Y"
# "Direction coordinates: A, B"
# "Width: Z degrees"
# "Range: Inner radius to Outer radius miles"

# And the function call becomes:
sector_coords = create_sector_polygon(
    center_lat=X,
    center_lon=Y,
    bearing_lat=A,
    bearing_lon=B,
    width_degrees=Z,
    min_radius_miles=inner_radius,
    max_radius_miles=outer_radius,
)
