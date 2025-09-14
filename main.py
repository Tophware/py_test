import folium
import math
import os
import webbrowser
from public_areas import PublicAreasOverlay

MAP_NAME = "veil.html"

# Configuration for public areas overlay
PUBLIC_AREAS_CONFIG = {
    "enabled": True,
    "area_types": ["park", "hiking", "recreation", "tourism", "water"],
    "padding_miles": 5,  # Extra padding around sectors when fetching public areas
}

# Dataset for sector configurations
SECTOR_DATASETS = [
    {
        "name": "Day 15 - New Hope Bridge",
        "center_lat": 40.364551,
        "center_lon": -74.950404,
        "bearing_lat": 40.365207,
        "bearing_lon": -74.947155,
        "width_degrees": 30,
        "min_radius_miles": 10,
        "max_radius_miles": 25,
        "rotation_degrees": 0,
        "colors": {
            "sector_outline": "blue",
            "sector_fill": "lightblue",
            "center_line": "red",
            "boundary_lines": "purple",
        },
        "marker_icon": "star",
        "marker_color": "red",
        "enabled": True,
    },
    {
        "name": "Day 18 - Towards High Voltage Lines",
        "center_lat": 40.447660,
        "center_lon": -74.530389,
        "bearing_lat": 40.448340,
        "bearing_lon": -74.530941,
        "width_degrees": 15,
        "min_radius_miles": 4,
        "max_radius_miles": 7,
        "rotation_degrees": 0,
        "colors": {
            "sector_outline": "green",
            "sector_fill": "lightgreen",
            "center_line": "orange",
            "boundary_lines": "darkgreen",
        },
        "marker_icon": "star",
        "marker_color": "green",
        "enabled": True,
    },
    # Add more sector configurations here as needed
]

# Additional map elements (circles, markers, etc.)
MAP_ELEMENTS = [
    {
        "type": "circle",
        "name": "4-mile Reference Circle",
        "lat": 40.484079,
        "lon": -74.575389,
        "radius_miles": 4,
        "color": "blue",
        "fill_color": "blue",
        "fill_opacity": 0.1,
        "weight": 2,
        "enabled": True,
    },
    {
        "type": "circle",
        "name": "Not in range",
        "lat": 40.447660,
        "lon": -74.530389,
        "radius_miles": 4,
        "color": "red",
        "fill_color": "red",
        "fill_opacity": 0.3,
        "weight": 2,
        "enabled": True,
    },
    {
        "type": "marker",
        "name": "Original Location",
        "lat": 40.484079,
        "lon": -74.575389,
        "icon": "info-sign",
        "color": "red",
        "popup": "Location: 40.484079, -74.575389",
        "tooltip": "Click for coordinates",
        "enabled": True,
    },
]


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


def add_sector_to_map(map_obj, sector_config):
    """
    Add a sector polygon with reference lines to the map based on configuration.

    Args:
        map_obj: Folium map object
        sector_config: Dictionary containing sector configuration
    """
    if not sector_config.get("enabled", True):
        return

    # Extract configuration
    center_lat = sector_config["center_lat"]
    center_lon = sector_config["center_lon"]
    bearing_lat = sector_config["bearing_lat"]
    bearing_lon = sector_config["bearing_lon"]
    width_degrees = sector_config["width_degrees"]
    min_radius_miles = sector_config["min_radius_miles"]
    max_radius_miles = sector_config["max_radius_miles"]
    rotation_degrees = sector_config.get("rotation_degrees", 0)
    colors = sector_config["colors"]
    name = sector_config["name"]

    # Create the sector polygon
    sector_coords = create_sector_polygon(
        center_lat=center_lat,
        center_lon=center_lon,
        bearing_lat=bearing_lat,
        bearing_lon=bearing_lon,
        width_degrees=width_degrees,
        min_radius_miles=min_radius_miles,
        max_radius_miles=max_radius_miles,
        rotation_degrees=rotation_degrees,
    )

    # Add the sector polygon to the map
    folium.Polygon(
        locations=sector_coords,
        popup=f"{name} Search Area ({min_radius_miles}-{max_radius_miles} miles, {width_degrees}° width)",
        tooltip=f"{name} Search Sector",
        color=colors["sector_outline"],
        weight=2,
        fill=True,
        fillColor=colors["sector_fill"],
        fillOpacity=0.1,
    ).add_to(map_obj)

    # Calculate bearing and reference line coordinates
    lat1, lon1 = math.radians(center_lat), math.radians(center_lon)
    lat2, lon2 = math.radians(bearing_lat), math.radians(bearing_lon)
    dlon = lon2 - lon1
    bearing_center = math.atan2(
        math.sin(dlon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon),
    )

    # Apply rotation
    bearing_center += math.radians(rotation_degrees)

    # Calculate reference line bearings
    half_width = math.radians(width_degrees / 2)
    bearing_left = bearing_center - half_width
    bearing_right = bearing_center + half_width

    # Convert miles to degrees
    min_radius_deg = min_radius_miles / 69.0
    max_radius_deg = max_radius_miles / 69.0

    # Red center line (center to max radius)
    center_line_end = [
        center_lat + max_radius_deg * math.cos(bearing_center),
        center_lon
        + max_radius_deg
        * math.sin(bearing_center)
        / math.cos(math.radians(center_lat)),
    ]
    folium.PolyLine(
        locations=[[center_lat, center_lon], center_line_end],
        popup=f"{name} - Center Bearing Line",
        tooltip="Center Bearing",
        color=colors["center_line"],
        weight=2,
        dashArray="8, 8",
        opacity=0.8,
    ).add_to(map_obj)

    # Purple left boundary line (center to min radius)
    left_line_end = [
        center_lat + min_radius_deg * math.cos(bearing_left),
        center_lon
        + min_radius_deg * math.sin(bearing_left) / math.cos(math.radians(center_lat)),
    ]
    folium.PolyLine(
        locations=[[center_lat, center_lon], left_line_end],
        popup=f"{name} - Left Boundary Line",
        tooltip="Left Boundary",
        color=colors["boundary_lines"],
        weight=2,
        dashArray="6, 6",
        opacity=0.8,
    ).add_to(map_obj)

    # Purple right boundary line (center to min radius)
    right_line_end = [
        center_lat + min_radius_deg * math.cos(bearing_right),
        center_lon
        + min_radius_deg * math.sin(bearing_right) / math.cos(math.radians(center_lat)),
    ]
    folium.PolyLine(
        locations=[[center_lat, center_lon], right_line_end],
        popup=f"{name} - Right Boundary Line",
        tooltip="Right Boundary",
        color=colors["boundary_lines"],
        weight=2,
        dashArray="6, 6",
        opacity=0.8,
    ).add_to(map_obj)

    # Add center marker
    folium.Marker(
        location=[center_lat, center_lon],
        popup=f"{name} (Center)",
        tooltip=f"{name} Center Point",
        icon=folium.Icon(
            color=sector_config["marker_color"], icon=sector_config["marker_icon"]
        ),
    ).add_to(map_obj)


def add_map_element_to_map(map_obj, element_config):
    """
    Add a map element (circle, marker, etc.) to the map based on configuration.

    Args:
        map_obj: Folium map object
        element_config: Dictionary containing element configuration
    """
    if not element_config.get("enabled", True):
        return

    element_type = element_config["type"]

    if element_type == "circle":
        # Convert miles to meters for Folium circle
        radius_meters = element_config["radius_miles"] * 1609.344

        folium.Circle(
            location=[element_config["lat"], element_config["lon"]],
            radius=radius_meters,
            popup=f"{element_config['name']} - {element_config['radius_miles']}-mile radius",
            tooltip=f"{element_config['radius_miles']}-mile radius",
            color=element_config["color"],
            weight=element_config["weight"],
            fill=True,
            fillColor=element_config["fill_color"],
            fillOpacity=element_config["fill_opacity"],
        ).add_to(map_obj)

    elif element_type == "marker":
        folium.Marker(
            location=[element_config["lat"], element_config["lon"]],
            popup=element_config["popup"],
            tooltip=element_config["tooltip"],
            icon=folium.Icon(
                color=element_config["color"], icon=element_config["icon"]
            ),
        ).add_to(map_obj)


def create_map_with_all_datasets():
    """
    Create a map with all enabled sectors and map elements from the datasets.
    """
    # Determine map center - use the first enabled sector or first map element
    map_center = None

    # Try to get center from first enabled sector
    for sector in SECTOR_DATASETS:
        if sector.get("enabled", True):
            map_center = [sector["center_lat"], sector["center_lon"]]
            break

    # If no sectors, use first enabled map element
    if map_center is None:
        for element in MAP_ELEMENTS:
            if element.get("enabled", True) and element["type"] in ["circle", "marker"]:
                map_center = [element["lat"], element["lon"]]
                break

    # Default center if nothing found
    if map_center is None:
        map_center = [40.484079, -74.575389]

    # Create base map
    m = folium.Map(location=map_center, zoom_start=11)

    # Add tile layers
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add public areas overlay if enabled
    if PUBLIC_AREAS_CONFIG.get("enabled", False):
        try:
            print("Loading public areas data...")
            overlay = PublicAreasOverlay()

            # Calculate bounds from sectors
            bounds = overlay.calculate_bounds_from_sectors(
                SECTOR_DATASETS, PUBLIC_AREAS_CONFIG.get("padding_miles", 5)
            )

            # Add public areas to map
            m = overlay.add_public_areas_to_map(
                m,
                bounds,
                PUBLIC_AREAS_CONFIG.get("area_types", ["park", "hiking", "recreation"]),
            )
            print("Public areas overlay added successfully!")

        except Exception as e:
            print(f"Warning: Could not load public areas overlay: {e}")

    # Add all map elements from dataset
    for element in MAP_ELEMENTS:
        add_map_element_to_map(m, element)

    # Add all sectors from dataset
    for sector in SECTOR_DATASETS:
        add_sector_to_map(m, sector)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map
    m.save(MAP_NAME)

    # Print summary
    enabled_sectors = [s for s in SECTOR_DATASETS if s.get("enabled", True)]
    enabled_elements = [e for e in MAP_ELEMENTS if e.get("enabled", True)]

    print(
        f"Map created with {len(enabled_sectors)} sector(s) and {len(enabled_elements)} element(s)"
    )
    for sector in enabled_sectors:
        print(
            f"  • {sector['name']}: {sector['min_radius_miles']}-{sector['max_radius_miles']} miles, {sector['width_degrees']}° width"
        )
    for element in enabled_elements:
        if element["type"] == "circle":
            print(f"  • {element['name']}: {element['radius_miles']}-mile radius")
        else:
            print(f"  • {element['name']}: {element['type']}")

    if PUBLIC_AREAS_CONFIG.get("enabled", False):
        print(
            f"  • Public areas overlay: {', '.join(PUBLIC_AREAS_CONFIG.get('area_types', []))}"
        )

    print(f"Map saved as '{MAP_NAME}'")
    # Create clickable link to open map in browser
    map_path = os.path.abspath(MAP_NAME)
    print(f"\nClick to open map: file://{map_path}")

    # Optionally auto-open in default browser
    # webbrowser.open(f"file://{map_path}")

    return m


if __name__ == "__main__":
    create_map_with_all_datasets()
