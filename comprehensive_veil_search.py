#!/usr/bin/env python3
"""
COMPREHENSIVE WEDGE SEARCH - THE VEIL
Complete analysis of historic sites, public areas, trails, and hiding spots within the search wedge.
Combines all previous searches into one comprehensive map for treasure hunting.
"""

import folium
import requests
from shapely.geometry import Point, Polygon
import json


def create_wedge_polygon(corners):
    """Create a Shapely polygon from corner coordinates for filtering."""
    # Convert corners to (lon, lat) for Shapely (note the order!)
    polygon_coords = [(corner[1], corner[0]) for corner in corners]
    return Polygon(polygon_coords)


def is_inside_wedge_with_buffer(lat, lon, wedge_polygon, buffer_km=0.5):
    """Check if a point is inside the wedge or within buffer distance."""
    point = Point(lon, lat)  # Shapely uses (lon, lat)

    # Check if inside wedge
    if wedge_polygon.contains(point):
        return True

    # Check if within buffer (approximately 0.5km = ~0.005 degrees)
    buffer_degrees = buffer_km * 0.01  # Rough conversion
    buffered_wedge = wedge_polygon.buffer(buffer_degrees)
    return buffered_wedge.contains(point)


def get_comprehensive_data(bounds, wedge_polygon):
    """
    Get all types of data: historic sites, public areas, trails, and points of interest.
    Filter to only include items inside or very close to the wedge.
    """
    south, west, north, east = bounds

    # Comprehensive query combining all previous searches
    query = f"""
    [out:json][timeout:120];
    (
      // === HISTORIC SITES ===
      way["historic"]({south},{west},{north},{east});
      node["historic"]({south},{west},{north},{east});
      relation["historic"]({south},{west},{north},{east});
      
      // Abandoned and ruins
      way["abandoned"]({south},{west},{north},{east});
      node["abandoned"]({south},{west},{north},{east});
      way["ruins"="yes"]({south},{west},{north},{east});
      node["ruins"="yes"]({south},{west},{north},{east});
      
      // Cemeteries
      way["landuse"="cemetery"]({south},{west},{north},{east});
      way["amenity"="grave_yard"]({south},{west},{north},{east});
      
      // Horse tracks and racing
      way["leisure"="horse_riding"]({south},{west},{north},{east});
      way["sport"="horse_racing"]({south},{west},{north},{east});
      node["name"~"Sullivan",i]({south},{west},{north},{east});
      way["name"~"Sullivan",i]({south},{west},{north},{east});
      
      // === LARGE PUBLIC AREAS ===
      // Parks and recreation
      way["leisure"="park"]["area"!="no"]({south},{west},{north},{east});
      relation["leisure"="park"]({south},{west},{north},{east});
      way["leisure"="recreation_ground"]({south},{west},{north},{east});
      
      // Forests and woods
      way["landuse"="forest"]({south},{west},{north},{east});
      relation["landuse"="forest"]({south},{west},{north},{east});
      way["natural"="wood"]({south},{west},{north},{east});
      relation["natural"="wood"]({south},{west},{north},{east});
      
      // Nature preserves
      way["leisure"="nature_reserve"]({south},{west},{north},{east});
      relation["leisure"="nature_reserve"]({south},{west},{north},{east});
      way["boundary"="protected_area"]({south},{west},{north},{east});
      relation["boundary"="protected_area"]({south},{west},{north},{east});
      
      // State and county parks
      way["leisure"="park"]["operator"~"[Ss]tate|[Cc]ounty"]({south},{west},{north},{east});
      relation["leisure"="park"]["operator"~"[Ss]tate|[Cc]ounty"]({south},{west},{north},{east});
      
      // === TRAILS AND PATHS ===
      // Hiking trails
      way["highway"="path"]({south},{west},{north},{east});
      way["highway"="footway"]({south},{west},{north},{east});
      way["highway"="track"]({south},{west},{north},{east});
      relation["route"="hiking"]({south},{west},{north},{east});
      
      // Biking trails
      way["highway"="cycleway"]({south},{west},{north},{east});
      relation["route"="bicycle"]({south},{west},{north},{east});
      
      // === NATURAL FEATURES ===
      // Water features
      way["natural"="water"]({south},{west},{north},{east});
      way["waterway"="river"]({south},{west},{north},{east});
      way["waterway"="stream"]({south},{west},{north},{east});
      
      // Natural hiding spots
      way["natural"="cave"]({south},{west},{north},{east});
      node["natural"="cave"]({south},{west},{north},{east});
      way["natural"="rock"]({south},{west},{north},{east});
      
      // === RECREATIONAL FACILITIES ===
      // Golf courses
      way["leisure"="golf_course"]({south},{west},{north},{east});
      
      // Sports facilities
      way["leisure"="sports_complex"]({south},{west},{north},{east});
      way["leisure"="pitch"]({south},{west},{north},{east});
      
      // === INFRASTRUCTURE ===
      // Parking areas (trail access points)
      way["amenity"="parking"]({south},{west},{north},{east});
      node["amenity"="parking"]({south},{west},{north},{east});
      
      // Bridges and structures
      way["bridge"="yes"]({south},{west},{north},{east});
      way["man_made"="bridge"]({south},{west},{north},{east});
    );
    out geom;
    """

    try:
        print("🔍 Gathering comprehensive data for the wedge...")
        response = requests.post(
            "https://overpass-api.de/api/interpreter", data=query, timeout=120
        )
        response.raise_for_status()
        data = response.json()

        elements = data.get("elements", [])
        print(f"📊 Found {len(elements)} total elements")

        # Filter elements to only those inside or near the wedge
        filtered_elements = []
        for element in elements:
            if is_element_in_wedge(element, wedge_polygon):
                filtered_elements.append(element)

        print(f"🎯 {len(filtered_elements)} elements are inside or near the wedge")

        # Categorize filtered elements
        categories = {
            "historic_sites": [],
            "cemeteries": [],
            "abandoned_ruins": [],
            "horse_tracks": [],
            "major_parks": [],
            "forests_woods": [],
            "nature_preserves": [],
            "state_county_parks": [],
            "hiking_trails": [],
            "biking_trails": [],
            "water_features": [],
            "natural_caves_rocks": [],
            "golf_courses": [],
            "sports_facilities": [],
            "parking_access": [],
            "bridges_structures": [],
        }

        for element in filtered_elements:
            category = classify_comprehensive_element(element)
            if category in categories:
                categories[category].append(element)

        return categories

    except Exception as e:
        print(f"❌ Error fetching comprehensive data: {e}")
        return {k: [] for k in categories.keys()}


def is_element_in_wedge(element, wedge_polygon):
    """Check if an element is inside or near the wedge."""
    if element["type"] == "node":
        return is_inside_wedge_with_buffer(
            element["lat"], element["lon"], wedge_polygon
        )

    elif element["type"] == "way" and "geometry" in element:
        # Check if any point of the way is inside the wedge
        for node in element["geometry"]:
            if is_inside_wedge_with_buffer(node["lat"], node["lon"], wedge_polygon):
                return True

    return False


def classify_comprehensive_element(element):
    """Classify elements into comprehensive categories."""
    tags = element.get("tags", {})
    name = tags.get("name", "").lower()

    # Historic sites
    if tags.get("historic"):
        if tags.get("historic") in ["memorial", "monument"]:
            return "historic_sites"
        else:
            return "historic_sites"

    # Cemeteries
    elif tags.get("landuse") == "cemetery" or tags.get("amenity") == "grave_yard":
        return "cemeteries"

    # Abandoned/ruins
    elif "abandoned" in str(tags) or tags.get("ruins") == "yes":
        return "abandoned_ruins"

    # Horse tracks
    elif (
        "sullivan" in name
        or "horse" in name
        or tags.get("sport") == "horse_racing"
        or tags.get("leisure") == "horse_riding"
    ):
        return "horse_tracks"

    # State/County parks
    elif tags.get("leisure") == "park" and tags.get("operator", "").lower() in [
        "state",
        "county",
    ]:
        return "state_county_parks"

    # Nature preserves
    elif (
        tags.get("leisure") == "nature_reserve"
        or tags.get("boundary") == "protected_area"
        or "preserve" in name
    ):
        return "nature_preserves"

    # Forests and woods
    elif tags.get("landuse") == "forest" or tags.get("natural") == "wood":
        return "forests_woods"

    # Major parks
    elif tags.get("leisure") == "park":
        return "major_parks"

    # Hiking trails
    elif (
        tags.get("highway") in ["path", "footway", "track"]
        or tags.get("route") == "hiking"
    ):
        return "hiking_trails"

    # Biking trails
    elif tags.get("highway") == "cycleway" or tags.get("route") == "bicycle":
        return "biking_trails"

    # Water features
    elif tags.get("natural") == "water" or tags.get("waterway") in ["river", "stream"]:
        return "water_features"

    # Natural caves and rocks
    elif tags.get("natural") in ["cave", "rock"]:
        return "natural_caves_rocks"

    # Golf courses
    elif tags.get("leisure") == "golf_course":
        return "golf_courses"

    # Sports facilities
    elif (
        tags.get("leisure") in ["sports_complex", "pitch"]
        or tags.get("leisure") == "recreation_ground"
    ):
        return "sports_facilities"

    # Parking and access
    elif tags.get("amenity") == "parking":
        return "parking_access"

    # Bridges and structures
    elif tags.get("bridge") == "yes" or tags.get("man_made") == "bridge":
        return "bridges_structures"

    else:
        return "historic_sites"  # Default fallback


def create_comprehensive_map(corners, data_categories):
    """Create the comprehensive map with all categories."""

    # Calculate center
    center_lat = sum(coord[0] for coord in corners) / len(corners)
    center_lon = sum(coord[1] for coord in corners) / len(corners)

    # Canister coordinates from story analysis
    canister_drop_point = [40.514417, -74.596033]  # Day 13 - Inside wedge!
    canister_landing_estimate = [40.707900, -74.380003]  # Outside wedge
    search_radius_miles = 0.5

    # Create map
    veil_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add tile layers
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(veil_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(veil_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic View",
        overlay=False,
        control=True,
    ).add_to(veil_map)

    # Category configurations
    category_configs = {
        "historic_sites": {
            "color": "purple",
            "fillColor": "lavender",
            "icon": "monument",
            "name": "🏛️ Historic Sites",
        },
        "cemeteries": {
            "color": "black",
            "fillColor": "lightgray",
            "icon": "cross",
            "name": "⛪ Cemeteries",
        },
        "abandoned_ruins": {
            "color": "gray",
            "fillColor": "lightgray",
            "icon": "home",
            "name": "🏚️ Abandoned/Ruins",
        },
        "horse_tracks": {
            "color": "darkred",
            "fillColor": "lightcoral",
            "icon": "horse",
            "name": "🐎 Horse Tracks",
        },
        "major_parks": {
            "color": "green",
            "fillColor": "lightgreen",
            "icon": "tree",
            "name": "🏞️ Major Parks",
        },
        "forests_woods": {
            "color": "darkgreen",
            "fillColor": "forestgreen",
            "icon": "tree",
            "name": "🌲 Forests & Woods",
        },
        "nature_preserves": {
            "color": "olive",
            "fillColor": "yellowgreen",
            "icon": "leaf",
            "name": "🦋 Nature Preserves",
        },
        "state_county_parks": {
            "color": "blue",
            "fillColor": "lightblue",
            "icon": "star",
            "name": "🏛️ State/County Parks",
        },
        "hiking_trails": {
            "color": "brown",
            "fillColor": "tan",
            "icon": "male",
            "name": "🥾 Hiking Trails",
        },
        "biking_trails": {
            "color": "orange",
            "fillColor": "lightyellow",
            "icon": "bicycle",
            "name": "🚴 Biking Trails",
        },
        "water_features": {
            "color": "cyan",
            "fillColor": "lightcyan",
            "icon": "tint",
            "name": "💧 Water Features",
        },
        "natural_caves_rocks": {
            "color": "darkblue",
            "fillColor": "lightblue",
            "icon": "mountain",
            "name": "🗿 Caves & Rocks",
        },
        "golf_courses": {
            "color": "lightgreen",
            "fillColor": "palegreen",
            "icon": "golf-ball",
            "name": "⛳ Golf Courses",
        },
        "sports_facilities": {
            "color": "red",
            "fillColor": "pink",
            "icon": "futbol-o",
            "name": "⚽ Sports Facilities",
        },
        "parking_access": {
            "color": "purple",
            "fillColor": "plum",
            "icon": "car",
            "name": "🅿️ Parking/Access",
        },
        "bridges_structures": {
            "color": "gray",
            "fillColor": "silver",
            "icon": "road",
            "name": "🌉 Bridges/Structures",
        },
    }

    total_items = 0

    # Add each category to the map
    for category, items in data_categories.items():
        if not items:
            continue

        config = category_configs.get(
            category,
            {
                "color": "gray",
                "fillColor": "lightgray",
                "icon": "map-marker",
                "name": category.title(),
            },
        )
        feature_group = folium.FeatureGroup(name=f"{config['name']} ({len(items)})")

        for item in items:
            add_item_to_map(feature_group, item, category, config)
            total_items += 1

        if len(items) > 0:
            feature_group.add_to(veil_map)

    # Add corner markers
    corner_labels = [
        "Day 18 Left (4-mile)",
        "Day 18 Right (4-mile)",
        "Day 15 cuts Day 18 (N)",
        "Day 15 cuts Day 18 (W)",
    ]
    colors = ["red", "blue", "green", "purple"]

    for i, (coord, label, color) in enumerate(zip(corners, corner_labels, colors)):
        folium.Marker(
            location=coord,
            popup=f"<b>Corner {i+1}: {label}</b><br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"Corner {i+1}: {label}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(veil_map)

    # Add wedge outline
    quad_coords = [corners[0], corners[1], corners[2], corners[3], corners[0]]
    folium.Polygon(
        locations=quad_coords,
        color="red",
        weight=4,
        fill=False,
        popup="<b>🎯 THE VEIL SEARCH AREA</b><br>Comprehensive treasure hunting map<br>Historic sites, public areas, trails, and hiding spots",
        tooltip="The Veil - Search Area Boundary",
    ).add_to(veil_map)

    # Add canister drop point (Day 13 - INSIDE WEDGE!)
    folium.Marker(
        location=canister_drop_point,
        popup=f'<b>🎯 CANISTER DROP POINT</b><br>Day 13: {canister_drop_point[0]:.6f}, {canister_drop_point[1]:.6f}<br><b>⚠️ INSIDE SEARCH WEDGE!</b><br>Bearing: 37°<br>Dimensions: 9.5" tall x 2 5/8" diameter<br>Mass: 1.5 KG<br>Look for publicly accessible wooded areas!',
        tooltip="🎯 CANISTER DROP POINT (Day 13)",
        icon=folium.Icon(color="orange", icon="bullseye", prefix="fa"),
    ).add_to(veil_map)

    # Add search zone circle around drop point (0.5 mile radius)
    folium.Circle(
        location=canister_drop_point,
        radius=804.672,  # 0.5 miles in meters
        popup=f"<b>🔍 PRIMARY SEARCH ZONE</b><br>0.5 mile radius around drop point<br><b>Focus on:</b><br>🌲 Wooded areas<br>🥾 Hiking trails<br>🏞️ Public parks<br>⛪ Cemetery sections",
        tooltip="🔍 0.5-mile Search Zone",
        color="orange",
        weight=3,
        fill=True,
        fillColor="yellow",
        fillOpacity=0.2,
    ).add_to(veil_map)

    # Add landing estimate (outside wedge, for reference)
    folium.Marker(
        location=canister_landing_estimate,
        popup=f"<b>📍 Landing Estimate</b><br>(Outside search wedge)<br>{canister_landing_estimate[0]:.6f}, {canister_landing_estimate[1]:.6f}<br>Distance: ~29.7 km from wedge",
        tooltip="📍 Landing Estimate (Reference)",
        icon=folium.Icon(color="gray", icon="map-marker", prefix="fa"),
    ).add_to(veil_map)

    # Add potential drop point marker
    potential_drop_point = [40.512783, -74.577009]
    folium.Marker(
        location=potential_drop_point,
        popup=f"<b>🎯 POTENTIAL DROP POINT</b><br>📍 {potential_drop_point[0]:.6f}, {potential_drop_point[1]:.6f}<br><b>⚠️ ALTERNATIVE CANISTER LOCATION</b><br>Check wooded areas within 2-mile radius<br>Focus on publicly accessible forests and trails",
        tooltip="🎯 Potential Drop Point",
        icon=folium.Icon(color="darkblue", icon="crosshairs", prefix="fa"),
    ).add_to(veil_map)

    # Add Sourland 37° drop path
    veil_map = add_sourland_drop_path(veil_map)

    # Add 2-mile radius circle around specified coordinates
    circle_center = [40.512783, -74.577009]
    veil_map = add_2mile_radius_circle(veil_map, circle_center)

    # Add layer control
    folium.LayerControl().add_to(veil_map)

    print(f"🗺️ Added {total_items} total items to The Veil map")
    return veil_map


def add_item_to_map(feature_group, item, category, config):
    """Add an item to the map with appropriate styling."""
    tags = item.get("tags", {})
    name = tags.get("name", f'Unnamed {category.replace("_", " ")}')

    # Create popup content with hiding potential
    popup_content = f"<b>{name}</b><br>"
    popup_content += f"🎯 Type: {category.replace('_', ' ').title()}<br>"

    # Add hiding/exploration potential
    hiding_potential = get_hiding_potential(category, tags)
    popup_content += hiding_potential

    # Add relevant tags
    relevant_tags = [
        "historic",
        "operator",
        "access",
        "surface",
        "description",
        "website",
    ]
    for tag in relevant_tags:
        if tag in tags and tags[tag]:
            popup_content += f"{tag.title()}: {tags[tag]}<br>"

    # Add to map based on geometry
    if item["type"] == "node":
        popup_content += f"📍 {item['lat']:.6f}, {item['lon']:.6f}"

        folium.Marker(
            location=[item["lat"], item["lon"]],
            popup=popup_content,
            tooltip=name,
            icon=folium.Icon(color=config["color"], icon=config["icon"], prefix="fa"),
        ).add_to(feature_group)

    elif item["type"] == "way" and "geometry" in item:
        coordinates = [[node["lat"], node["lon"]] for node in item["geometry"]]

        if len(coordinates) > 2 and coordinates[0] == coordinates[-1]:
            # Polygon/area
            folium.Polygon(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=config["color"],
                weight=2,
                fill=True,
                fillColor=config["fillColor"],
                fillOpacity=0.3,
            ).add_to(feature_group)
        else:
            # Line/path
            folium.PolyLine(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=config["color"],
                weight=3,
                opacity=0.7,
            ).add_to(feature_group)


def add_sourland_drop_path(veil_map):
    """Add the 37° drop line from Sourland release point"""

    # Release point and trajectory coordinates
    trajectory_points = [
        {"distance": "Release Point", "coords": [40.453399, -74.738749]},
        {"distance": "~5 km out", "coords": [40.489305, -74.703167]},
        {"distance": "~10 km out", "coords": [40.525200, -74.667546]},
        {"distance": "~15 km out", "coords": [40.561084, -74.631888]},
        {"distance": "~20 km out", "coords": [40.596958, -74.596191]},
    ]

    # Create feature group for the drop path
    drop_path_group = folium.FeatureGroup(name="🚁 Sourland 37° Drop Path")

    # Extract coordinates for the path line
    path_coords = [point["coords"] for point in trajectory_points]

    # Add the trajectory line
    folium.PolyLine(
        locations=path_coords,
        color="darkred",
        weight=4,
        opacity=0.8,
        dash_array="10,5",
        popup="<b>🚁 Sourland 37° Drop Trajectory</b><br>NE trajectory from release point<br>Track canister potential path",
        tooltip="37° NE trajectory from Sourland release point",
    ).add_to(drop_path_group)

    # Add markers for each trajectory point
    for i, point in enumerate(trajectory_points):
        icon_color = "red" if i == 0 else "darkred"
        icon_symbol = "play" if i == 0 else "circle"

        popup_content = f"<b>🚁 {point['distance']}</b><br>"
        popup_content += f"📍 {point['coords'][0]:.6f}, {point['coords'][1]:.6f}<br>"

        if i == 0:
            popup_content += "🚁 <b>SOURLAND RELEASE POINT</b><br>"
            popup_content += "Starting point of 37° NE trajectory"
        else:
            popup_content += f"🎯 Trajectory point {point['distance']}<br>"
            popup_content += "Projected canister path along 37° bearing"

        folium.Marker(
            location=point["coords"],
            popup=popup_content,
            tooltip=f"🚁 {point['distance']}",
            icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix="fa"),
        ).add_to(drop_path_group)

    drop_path_group.add_to(veil_map)
    return veil_map


def add_2mile_radius_circle(veil_map, center_coords):
    """Add a 2-mile radius circle around specified coordinates"""

    # Create feature group for the circle
    circle_group = folium.FeatureGroup(name="🎯 2-Mile Search Radius")

    # Add the 2-mile radius circle
    folium.Circle(
        location=center_coords,
        radius=3218.688,  # 2 miles in meters
        popup=f"<b>🎯 2-MILE SEARCH RADIUS</b><br>Center: {center_coords[0]:.6f}, {center_coords[1]:.6f}<br>Radius: 2 miles<br>Focus search within this area",
        tooltip="🎯 2-Mile Search Radius",
        color="blue",
        weight=3,
        fill=True,
        fillColor="lightblue",
        fillOpacity=0.1,
    ).add_to(circle_group)

    # Add center marker
    folium.Marker(
        location=center_coords,
        popup=f"<b>🎯 SEARCH CENTER</b><br>📍 {center_coords[0]:.6f}, {center_coords[1]:.6f}<br>2-mile radius search area",
        tooltip="🎯 Search Center",
        icon=folium.Icon(color="blue", icon="crosshairs", prefix="fa"),
    ).add_to(circle_group)

    circle_group.add_to(veil_map)
    return veil_map


def get_hiding_potential(category, tags):
    """Get hiding potential analysis for each category."""
    if category == "cemeteries":
        return "🎯 HIDING POTENTIAL: EXCELLENT - Secluded sections, old trees<br>"
    elif category == "forests_woods":
        return "🌲 HIDING POTENTIAL: EXCELLENT - Natural cover, varied terrain<br>"
    elif category == "abandoned_ruins":
        return "🏚️ HIDING POTENTIAL: VERY HIGH - Forgotten areas, structures<br>"
    elif category == "horse_tracks":
        return (
            "🐎 HIDING POTENTIAL: HIGH - Historic track areas, old infrastructure<br>"
        )
    elif category == "natural_caves_rocks":
        return "🗿 HIDING POTENTIAL: EXCELLENT - Natural concealment<br>"
    elif category == "hiking_trails":
        return "🥾 EXPLORATION: Good trail access, look for offshoots<br>"
    elif category == "state_county_parks":
        return "🏛️ EXPLORATION: EXCELLENT - Large area, multiple trails<br>"
    elif category == "nature_preserves":
        return "🦋 EXPLORATION: HIGH - Protected trails, less crowded<br>"
    elif category == "water_features":
        return "💧 EXPLORATION: Good - Waterside areas, bridge crossings<br>"
    elif category == "golf_courses":
        return "⛳ EXPLORATION: Moderate - Wooded edges, less monitored areas<br>"
    else:
        return "📍 EXPLORATION: Variable - Check access and terrain<br>"


def main():
    print("🎯 THE VEIL - COMPREHENSIVE WEDGE SEARCH")
    print("🔍 All historic sites, public areas, trails, and hiding spots")
    print("🏆 The ultimate treasure hunting map")
    print("=" * 80)

    # The 4 precise corner coordinates
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    # Canister coordinates from story analysis
    canister_drop_point = [40.514417, -74.596033]  # Day 13 - INSIDE WEDGE!

    # Create wedge polygon for filtering
    wedge_polygon = create_wedge_polygon(corners)

    # Calculate bounds with small buffer
    lats = [corner[0] for corner in corners]
    lons = [corner[1] for corner in corners]

    south, north = min(lats) - 0.005, max(lats) + 0.005
    west, east = min(lons) - 0.005, max(lons) + 0.005
    bounds = (south, west, north, east)

    # Get comprehensive data
    data_categories = get_comprehensive_data(bounds, wedge_polygon)

    # Create the comprehensive map
    veil_map = create_comprehensive_map(corners, data_categories)

    # Save as veil.html
    output_file = "veil.html"
    veil_map.save(output_file)

    print(f"\n🗺️ THE VEIL saved as: {output_file}")

    # Print summary
    print(f"\n📊 COMPREHENSIVE SUMMARY:")
    total_found = 0
    for category, items in data_categories.items():
        if items:
            total_found += len(items)
            print(f"   {category.replace('_', ' ').title()}: {len(items)}")

    print(f"\n🎯 Total items in The Veil: {total_found}")
    print(f"\n🏆 THE VEIL contains everything you need:")
    print(f"   � CANISTER DROP POINT (Day 13) - INSIDE SEARCH AREA!")
    print(f"   🔍 0.5-mile search zone around drop point")
    print(f"   �🏛️ Historic sites and ruins for exploration")
    print(f"   🌲 Forests and woods for natural cover")
    print(f"   ⛪ Cemeteries with secluded sections")
    print(f"   🥾 Trail networks for access")
    print(f"   🎯 All filtered to your precise search wedge!")
    print(f"\n🌲 FOCUS YOUR SEARCH ON:")
    print(f"   • Publicly accessible wooded areas near {canister_drop_point}")
    print(f"   • Forest trails and hiking paths")
    print(f"   • Cemetery wooded sections")
    print(f"   • Parks with natural cover")

    return veil_map


if __name__ == "__main__":
    main()
