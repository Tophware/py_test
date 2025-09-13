import folium
import math

MAP_NAME = "veil.html"


def create_sector_polygon(
    center_lat,
    center_lon,
    bearing_lat,
    bearing_lon,
    width_degrees,
    min_radius_miles,
    max_radius_miles,
):
    """
    Create a sector polygon between two circles bounded by angular lines.

    Args:
        center_lat, center_lon: Center point coordinates (where circles are drawn)
        bearing_lat, bearing_lon: Second point to determine direction of center line
        width_degrees: Total angular width in degrees (will be split evenly on both sides)
        min_radius_miles: Inner radius in miles
        max_radius_miles: Outer radius in miles

    Returns:
        List of [lat, lon] coordinates forming the polygon
    """
    # Calculate bearing from center point to bearing point
    lat1, lon1 = math.radians(center_lat), math.radians(center_lon)
    lat2, lon2 = math.radians(bearing_lat), math.radians(bearing_lon)

    dlon = lon2 - lon1
    bearing_center = math.atan2(
        math.sin(dlon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon),
    )

    # Convert degrees to radians
    half_width = math.radians(width_degrees / 2)

    # Calculate left and right bearings
    bearing_left = bearing_center - half_width
    bearing_right = bearing_center + half_width

    # Convert miles to approximate degrees (1 degree ≈ 69 miles)
    min_radius_deg = min_radius_miles / 69.0
    max_radius_deg = max_radius_miles / 69.0

    # Create polygon points
    polygon_points = []

    # Start at center
    polygon_points.append([center_lat, center_lon])

    # Arc along minimum radius from left to right
    num_arc_points = 20  # Number of points to approximate the arc
    for i in range(num_arc_points + 1):
        # Interpolate bearing from left to right
        bearing = bearing_left + (bearing_right - bearing_left) * i / num_arc_points

        # Calculate point on inner circle
        lat = center_lat + min_radius_deg * math.cos(bearing)
        lon = center_lon + min_radius_deg * math.sin(bearing) / math.cos(
            math.radians(center_lat)
        )
        polygon_points.append([lat, lon])

    # Arc along maximum radius from right to left
    for i in range(num_arc_points + 1):
        # Interpolate bearing from right to left
        bearing = bearing_right - (bearing_right - bearing_left) * i / num_arc_points

        # Calculate point on outer circle
        lat = center_lat + max_radius_deg * math.cos(bearing)
        lon = center_lon + max_radius_deg * math.sin(bearing) / math.cos(
            math.radians(center_lat)
        )
        polygon_points.append([lat, lon])

    # Close the polygon by returning to center
    polygon_points.append([center_lat, center_lon])

    return polygon_points


def create_map_with_marker_and_circle():
    # Coordinates for the marker
    lat, lon = 40.484079, -74.575389

    # Create base map centered on the coordinates
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Add street view (default)
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(m)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add marker at the specified coordinates
    folium.Marker(
        location=[lat, lon],
        popup=f"Location: {lat}, {lon}",
        tooltip="Click for coordinates",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Add 4-mile circle (4 miles = 6437.38 meters)
    # 1 mile = 1609.344 meters, so 4 miles = 6437.376 meters
    circle_radius = 4 * 1609.344  # 4 miles in meters

    folium.Circle(
        location=[lat, lon],
        radius=circle_radius,
        popup=f"4-mile radius circle",
        tooltip="4-mile radius",
        color="blue",
        weight=2,
        fill=True,
        fillColor="blue",
        fillOpacity=0.3,  # Transparent blue
    ).add_to(m)

    # Day 15 - New Hope Bridge: Create a line starting from coordinates,
    # passing through second point, and extending for 25 miles
    import math

    # Starting point and direction point
    start_lat, start_lon = 40.364551, -74.950404
    direction_lat, direction_lon = 40.365207, -74.947155

    # Calculate bearing (direction) from start to direction point
    lat1, lon1 = math.radians(start_lat), math.radians(start_lon)
    lat2, lon2 = math.radians(direction_lat), math.radians(direction_lon)

    dlon = lon2 - lon1
    bearing = math.atan2(
        math.sin(dlon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon),
    )

    # Convert 25 miles to degrees (approximately)
    # 1 degree latitude ≈ 69 miles, so 25 miles ≈ 0.362 degrees
    distance_deg = 25 / 69.0

    # Calculate end point 25 miles from start point in the same direction
    end_lat = start_lat + distance_deg * math.cos(bearing)
    end_lon = start_lon + distance_deg * math.sin(bearing) / math.cos(
        math.radians(start_lat)
    )

    # Create line coordinates
    line_coords = [
        [start_lat, start_lon],
        [direction_lat, direction_lon],
        [end_lat, end_lon],
    ]

    # Add the line to the map
    folium.PolyLine(
        locations=line_coords,
        popup="Day 15 - New Hope Bridge (25 mile extension)",
        tooltip="Day 15 - New Hope Bridge",
        color="green",
        weight=3,
        opacity=0.8,
    ).add_to(m)

    # Add markers for the key points
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Day 15 Start: New Hope Bridge",
        tooltip="Start Point",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(m)

    folium.Marker(
        location=[direction_lat, direction_lon],
        popup="Day 15 Direction Point",
        tooltip="Direction Point",
        icon=folium.Icon(color="orange", icon="arrow-right"),
    ).add_to(m)

    # Add two additional lines with 15-degree spread on either side
    # Convert 15 degrees to radians
    angle_spread = math.radians(15)

    # Calculate bearings for left and right lines
    bearing_left = bearing - angle_spread  # 15 degrees to the left
    bearing_right = bearing + angle_spread  # 15 degrees to the right

    # Calculate end points for left line (15 degrees left of original)
    end_lat_left = start_lat + distance_deg * math.cos(bearing_left)
    end_lon_left = start_lon + distance_deg * math.sin(bearing_left) / math.cos(
        math.radians(start_lat)
    )

    # Calculate end points for right line (15 degrees right of original)
    end_lat_right = start_lat + distance_deg * math.cos(bearing_right)
    end_lon_right = start_lon + distance_deg * math.sin(bearing_right) / math.cos(
        math.radians(start_lat)
    )

    # Create line coordinates for left line
    line_coords_left = [[start_lat, start_lon], [end_lat_left, end_lon_left]]

    # Create line coordinates for right line
    line_coords_right = [[start_lat, start_lon], [end_lat_right, end_lon_right]]

    # Add left line (15 degrees counter-clockwise)
    folium.PolyLine(
        locations=line_coords_left,
        popup="Day 15 - New Hope Bridge (Left 15°, 25 miles)",
        tooltip="Day 15 - Left Line (-15°)",
        color="darkgreen",
        weight=2,
        opacity=0.6,
        dashArray="5, 5",  # Dashed line to distinguish from main line
    ).add_to(m)

    # Add right line (15 degrees clockwise)
    folium.PolyLine(
        locations=line_coords_right,
        popup="Day 15 - New Hope Bridge (Right 15°, 25 miles)",
        tooltip="Day 15 - Right Line (+15°)",
        color="darkgreen",
        weight=2,
        opacity=0.6,
        dashArray="5, 5",  # Dashed line to distinguish from main line
    ).add_to(m)

    # Create Day 15 New Hope Bridge sector polygon (10-25 mile range, 30-degree width)
    sector_coords = create_sector_polygon(
        center_lat=start_lat,
        center_lon=start_lon,
        bearing_lat=direction_lat,
        bearing_lon=direction_lon,
        width_degrees=30,  # 30-degree total width (15° each side)
        min_radius_miles=10,  # Inner radius 10 miles
        max_radius_miles=25,  # Outer radius 25 miles
    )

    # Add the sector polygon to the map
    folium.Polygon(
        locations=sector_coords,
        popup="Day 15 - New Hope Bridge Search Area (10-25 miles, 30° width)",
        tooltip="Day 15 Search Sector",
        color="green",
        weight=2,
        fill=True,
        fillColor="lightgreen",
        fillOpacity=0.2,
    ).add_to(m)

    # Update the marker to be more specific
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Day 15 - New Hope Bridge (Origin)",
        tooltip="Day 15 Origin Point",
        icon=folium.Icon(color="green", icon="star"),
    ).add_to(m)

    # Add layer control to switch between street/satellite views
    folium.LayerControl().add_to(m)

    # Save the map
    m.save(MAP_NAME)
    print(f"Map created with marker at {lat}, {lon}")
    print(f"Blue transparent 4-mile circle added")
    print(f"Map saved as '{MAP_NAME}'")

    return m


if __name__ == "__main__":
    create_map_with_marker_and_circle()
