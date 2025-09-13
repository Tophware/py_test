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
    rotation_degrees=0,
):
    """
    Create a sector polygon between two circles bounded by angular lines.

    Args:
        center_lat, center_lon: Center point coordinates (where circles are drawn)
        bearing_lat, bearing_lon: Second point to determine direction of center line
        width_degrees: Total angular width in degrees (will be split evenly on both sides)
        min_radius_miles: Inner radius in miles
        max_radius_miles: Outer radius in miles
        rotation_degrees: Additional rotation in degrees around center point (positive = clockwise)

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

    # Apply rotation to the center bearing
    rotation_rad = math.radians(rotation_degrees)
    bearing_center += rotation_rad

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

    # Close polygon back to start of min radius arc (no center point)
    bearing = bearing_left
    lat = center_lat + min_radius_deg * math.cos(bearing)
    lon = center_lon + min_radius_deg * math.sin(bearing) / math.cos(
        math.radians(center_lat)
    )
    polygon_points.append([lat, lon])

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

    # Day 15 - New Hope Bridge: Create clean sector with reference lines
    import math

    # Starting point and direction point
    start_lat, start_lon = 40.364551, -74.950404
    direction_lat, direction_lon = 40.365207, -74.947155

    # Create the sector polygon (10-25 mile range, 30-degree width)
    sector_coords = create_sector_polygon(
        center_lat=start_lat,
        center_lon=start_lon,
        bearing_lat=direction_lat,
        bearing_lon=direction_lon,
        width_degrees=30,  # 30-degree total width (15° each side)
        min_radius_miles=10,  # Inner radius 10 miles
        max_radius_miles=25,  # Outer radius 25 miles
        # No rotation parameter - using default 0
    )

    # Add the sector polygon to the map
    folium.Polygon(
        locations=sector_coords,
        popup="Day 15 - New Hope Bridge Search Area (10-25 miles, 30° width)",
        tooltip="Day 15 Search Sector",
        color="blue",  # Blue outline
        weight=2,
        fill=True,
        fillColor="lightblue",  # Light blue fill
        fillOpacity=0.4,
    ).add_to(m)

    # Calculate bearing and reference line coordinates
    lat1, lon1 = math.radians(start_lat), math.radians(start_lon)
    lat2, lon2 = math.radians(direction_lat), math.radians(direction_lon)
    dlon = lon2 - lon1
    bearing_center = math.atan2(
        math.sin(dlon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon),
    )

    # Calculate reference line bearings
    half_width = math.radians(30 / 2)  # 15 degrees each side
    bearing_left = bearing_center - half_width
    bearing_right = bearing_center + half_width

    # Convert miles to degrees
    min_radius_deg = 10 / 69.0
    max_radius_deg = 25 / 69.0

    # Red center line (center to max radius)
    center_line_end = [
        start_lat + max_radius_deg * math.cos(bearing_center),
        start_lon + max_radius_deg * math.sin(bearing_center) / math.cos(math.radians(start_lat))
    ]
    folium.PolyLine(
        locations=[[start_lat, start_lon], center_line_end],
        popup="Center Bearing Line",
        tooltip="Center Bearing",
        color="red",
        weight=2,
        dashArray="8, 8",
        opacity=0.8,
    ).add_to(m)

    # Purple left boundary line (center to min radius)
    left_line_end = [
        start_lat + min_radius_deg * math.cos(bearing_left),
        start_lon + min_radius_deg * math.sin(bearing_left) / math.cos(math.radians(start_lat))
    ]
    folium.PolyLine(
        locations=[[start_lat, start_lon], left_line_end],
        popup="Left Boundary Line (-15°)",
        tooltip="Left Boundary",
        color="purple",
        weight=2,
        dashArray="6, 6",
        opacity=0.8,
    ).add_to(m)

    # Purple right boundary line (center to min radius)
    right_line_end = [
        start_lat + min_radius_deg * math.cos(bearing_right),
        start_lon + min_radius_deg * math.sin(bearing_right) / math.cos(math.radians(start_lat))
    ]
    folium.PolyLine(
        locations=[[start_lat, start_lon], right_line_end],
        popup="Right Boundary Line (+15°)",
        tooltip="Right Boundary",
        color="purple",
        weight=2,
        dashArray="6, 6",
        opacity=0.8,
    ).add_to(m)

    # Add center marker
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Day 15 - New Hope Bridge (Center)",
        tooltip="Day 15 Center Point",
        icon=folium.Icon(color="red", icon="star"),
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


def create_rotatable_sector_demo():
    """
    Demonstrates how to create multiple rotated versions of the same sector polygon
    for comparison and area isolation.
    """
    # Starting point for Day 15 - New Hope Bridge
    start_lat, start_lon = 40.364551, -74.950404
    direction_lat, direction_lon = 40.365207, -74.947155

    # Create base map
    m = folium.Map(location=[start_lat, start_lon], zoom_start=11)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Create the original sector (no rotation)
    original_sector = create_sector_polygon(
        center_lat=start_lat,
        center_lon=start_lon,
        bearing_lat=direction_lat,
        bearing_lon=direction_lon,
        width_degrees=30,
        min_radius_miles=10,
        max_radius_miles=25,
        rotation_degrees=0,  # No rotation
    )

    # Add original sector
    folium.Polygon(
        locations=original_sector,
        popup="Original Sector (0° rotation)",
        tooltip="Day 15 Original",
        color="green",
        weight=2,
        fill=True,
        fillColor="lightgreen",
        fillOpacity=0.3,
    ).add_to(m)

    # Create rotated versions for comparison
    rotation_angles = [45, 90, -45, -90]  # Different rotation angles to try
    colors = ["blue", "red", "orange", "purple"]

    for i, rotation in enumerate(rotation_angles):
        rotated_sector = create_sector_polygon(
            center_lat=start_lat,
            center_lon=start_lon,
            bearing_lat=direction_lat,
            bearing_lon=direction_lon,
            width_degrees=30,
            min_radius_miles=10,
            max_radius_miles=25,
            rotation_degrees=rotation,
        )

        folium.Polygon(
            locations=rotated_sector,
            popup=f"Rotated Sector ({rotation}° rotation)",
            tooltip=f"Rotated {rotation}°",
            color=colors[i],
            weight=1,
            fill=True,
            fillColor=colors[i],
            fillOpacity=0.15,
        ).add_to(m)

    # Add center marker
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Day 15 - New Hope Bridge (Rotation Center)",
        tooltip="Rotation Center",
        icon=folium.Icon(color="red", icon="star"),
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the rotated demo map
    demo_map_name = "rotatable_sector_demo.html"
    m.save(demo_map_name)
    print(f"Rotatable sector demo saved as '{demo_map_name}'")
    print(
        "This shows the original sector plus rotated versions at 45°, 90°, -45°, and -90°"
    )

    return m


def create_custom_rotated_sector(rotation_degrees):
    """
    Create a map with a sector rotated by a specific angle.

    Args:
        rotation_degrees: Angle to rotate the sector (positive = clockwise)
    """
    # Starting point for Day 15 - New Hope Bridge
    start_lat, start_lon = 40.364551, -74.950404
    direction_lat, direction_lon = 40.365207, -74.947155

    # Create base map
    m = folium.Map(location=[start_lat, start_lon], zoom_start=11)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Create the rotated sector
    rotated_sector = create_sector_polygon(
        center_lat=start_lat,
        center_lon=start_lon,
        bearing_lat=direction_lat,
        bearing_lon=direction_lon,
        width_degrees=30,
        min_radius_miles=10,
        max_radius_miles=25,
        rotation_degrees=rotation_degrees,
    )

    # Add rotated sector
    folium.Polygon(
        locations=rotated_sector,
        popup=f"Custom Rotated Sector ({rotation_degrees}° rotation)",
        tooltip=f"Rotated {rotation_degrees}°",
        color="blue",
        weight=2,
        fill=True,
        fillColor="lightblue",
        fillOpacity=0.4,
    ).add_to(m)

    # Add center marker
    folium.Marker(
        location=[start_lat, start_lon],
        popup=f"Day 15 - Rotated {rotation_degrees}°",
        tooltip="Rotation Center",
        icon=folium.Icon(color="blue", icon="star"),
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the custom rotated map
    custom_map_name = f"sector_rotated_{rotation_degrees}deg.html"
    m.save(custom_map_name)
    print(f"Custom rotated sector ({rotation_degrees}°) saved as '{custom_map_name}'")

    return m
