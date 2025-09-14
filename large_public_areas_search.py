#!/usr/bin/env python3
"""
LARGE PUBLIC AREAS SEARCH
Identify substantial public spaces like entire parks, forests, preserves,
and other large areas open to the public for exploration and hiding spots.
"""

import folium
import requests
import json


def get_large_public_areas(bounds):
    """
    Get large public areas like parks, forests, preserves, recreation areas.

    Args:
        bounds: Tuple of (south, west, north, east) coordinates

    Returns:
        Dictionary with categorized large public areas
    """
    south, west, north, east = bounds

    # Query for substantial public areas
    query = f"""
    [out:json][timeout:60];
    (
      // Large parks and recreation areas
      way["leisure"="park"]["area"!="no"]({south},{west},{north},{east});
      relation["leisure"="park"]({south},{west},{north},{east});
      way["leisure"="recreation_ground"]({south},{west},{north},{east});
      
      // Nature preserves and protected areas
      way["leisure"="nature_reserve"]({south},{west},{north},{east});
      relation["leisure"="nature_reserve"]({south},{west},{north},{east});
      way["boundary"="protected_area"]({south},{west},{north},{east});
      relation["boundary"="protected_area"]({south},{west},{north},{east});
      
      // Forests and wooded areas
      way["landuse"="forest"]({south},{west},{north},{east});
      relation["landuse"="forest"]({south},{west},{north},{east});
      way["natural"="wood"]({south},{west},{north},{east});
      relation["natural"="wood"]({south},{west},{north},{east});
      
      // State and county parks
      way["leisure"="park"]["operator"~"[Ss]tate|[Cc]ounty|[Gg]overnment"]({south},{west},{north},{east});
      relation["leisure"="park"]["operator"~"[Ss]tate|[Cc]ounty|[Gg]overnment"]({south},{west},{north},{east});
      
      // Wildlife management areas
      way["protect_class"]({south},{west},{north},{east});
      relation["protect_class"]({south},{west},{north},{east});
      
      // Large recreational complexes
      way["leisure"="sports_complex"]({south},{west},{north},{east});
      way["leisure"="golf_course"]({south},{west},{north},{east});
      
      // Greenways and trail systems
      way["highway"="path"]["name"]({south},{west},{north},{east});
      way["route"="hiking"]({south},{west},{north},{east});
      relation["route"="hiking"]({south},{west},{north},{east});
      
      // Water recreation areas
      way["leisure"="swimming_area"]({south},{west},{north},{east});
      way["natural"="water"]["leisure"]({south},{west},{north},{east});
      
      // Public open space
      way["landuse"="recreation_ground"]({south},{west},{north},{east});
      way["leisure"="common"]({south},{west},{north},{east});
      
      // Specific large park types
      way["leisure"="dog_park"]["area"!="no"]({south},{west},{north},{east});
      way["amenity"="public_bookcase"]({south},{west},{north},{east}); // Often in parks
    );
    out geom;
    """

    try:
        print("🌳 Searching for large public areas...")
        response = requests.post(
            "https://overpass-api.de/api/interpreter", data=query, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # Categorize the findings
        categories = {
            "major_parks": [],
            "forests_woods": [],
            "nature_preserves": [],
            "state_county_parks": [],
            "recreation_areas": [],
            "golf_courses": [],
            "trail_systems": [],
            "water_recreation": [],
            "open_spaces": [],
        }

        for element in data.get("elements", []):
            category = classify_public_area(element)
            if category in categories:
                categories[category].append(element)

        return categories

    except Exception as e:
        print(f"⚠️ Error fetching public area data: {e}")
        return {k: [] for k in categories.keys()}


def classify_public_area(element):
    """Classify public areas by type and size."""
    tags = element.get("tags", {})
    name = tags.get("name", "").lower()

    # State/County parks
    if (
        tags.get("operator", "").lower() in ["state", "county"]
        or "state" in name
        or "county" in name
    ):
        return "state_county_parks"

    # Nature preserves and protected areas
    elif (
        tags.get("leisure") == "nature_reserve"
        or tags.get("boundary") == "protected_area"
        or "preserve" in name
        or "wildlife" in name
    ):
        return "nature_preserves"

    # Forests and woods
    elif tags.get("landuse") == "forest" or tags.get("natural") == "wood":
        return "forests_woods"

    # Golf courses
    elif tags.get("leisure") == "golf_course":
        return "golf_courses"

    # Trail systems and greenways
    elif (
        tags.get("route") == "hiking"
        or (tags.get("highway") == "path" and tags.get("name"))
        or "trail" in name
        or "greenway" in name
    ):
        return "trail_systems"

    # Water recreation
    elif tags.get("leisure") == "swimming_area" or (
        tags.get("natural") == "water" and tags.get("leisure")
    ):
        return "water_recreation"

    # Recreation areas and complexes
    elif (
        tags.get("leisure") in ["recreation_ground", "sports_complex"]
        or tags.get("landuse") == "recreation_ground"
    ):
        return "recreation_areas"

    # General open spaces
    elif tags.get("leisure") == "common" or "common" in name or "green" in name:
        return "open_spaces"

    # Major parks (default for parks)
    else:
        return "major_parks"


def calculate_area_size(element):
    """Estimate the size category of an area."""
    if element["type"] == "way" and "geometry" in element:
        # Simple estimation based on bounding box
        coords = element["geometry"]
        if len(coords) > 3:
            lats = [c["lat"] for c in coords]
            lons = [c["lon"] for c in coords]
            lat_span = max(lats) - min(lats)
            lon_span = max(lons) - min(lons)

            # Rough size estimation
            if lat_span > 0.01 or lon_span > 0.01:
                return "LARGE"
            elif lat_span > 0.005 or lon_span > 0.005:
                return "MEDIUM"
            else:
                return "SMALL"
    return "UNKNOWN"


def add_public_areas_overlay(map_obj, bounds):
    """Add large public areas overlay to the map."""
    public_data = get_large_public_areas(bounds)

    # Color scheme for different types of public areas
    category_colors = {
        "major_parks": {
            "color": "green",
            "fillColor": "lightgreen",
            "name": "🏞️ Major Parks",
        },
        "forests_woods": {
            "color": "darkgreen",
            "fillColor": "forestgreen",
            "name": "🌲 Forests & Woods",
        },
        "nature_preserves": {
            "color": "olive",
            "fillColor": "yellowgreen",
            "name": "🦋 Nature Preserves",
        },
        "state_county_parks": {
            "color": "blue",
            "fillColor": "lightblue",
            "name": "🏛️ State/County Parks",
        },
        "recreation_areas": {
            "color": "orange",
            "fillColor": "lightyellow",
            "name": "⚽ Recreation Areas",
        },
        "golf_courses": {
            "color": "lightgreen",
            "fillColor": "palegreen",
            "name": "⛳ Golf Courses",
        },
        "trail_systems": {
            "color": "brown",
            "fillColor": "tan",
            "name": "🥾 Trail Systems",
        },
        "water_recreation": {
            "color": "cyan",
            "fillColor": "lightcyan",
            "name": "🏊 Water Recreation",
        },
        "open_spaces": {
            "color": "purple",
            "fillColor": "lavender",
            "name": "🌿 Open Spaces",
        },
    }

    total_areas = 0
    area_details = {}

    for category, items in public_data.items():
        if not items:
            continue

        colors = category_colors.get(
            category,
            {"color": "gray", "fillColor": "lightgray", "name": category.title()},
        )
        feature_group = folium.FeatureGroup(name=f"{colors['name']} ({len(items)})")

        category_areas = []
        for item in items:
            area_info = add_public_area_to_map(feature_group, item, category, colors)
            if area_info:
                category_areas.append(area_info)
            total_areas += 1

        if len(items) > 0:
            feature_group.add_to(map_obj)
            area_details[category] = category_areas

    print(f"🏞️ Added {total_areas} large public areas")
    return map_obj, area_details


def add_public_area_to_map(feature_group, item, category, colors):
    """Add a public area to the feature group with detailed information."""
    tags = item.get("tags", {})
    name = tags.get("name", f'Unnamed {category.replace("_", " ")}')
    area_size = calculate_area_size(item)

    # Create detailed popup for public area analysis
    popup_content = f"<b>{name}</b><br>"
    popup_content += f"🌳 Type: {category.replace('_', ' ').title()}<br>"
    popup_content += f"📏 Size: {area_size}<br>"

    # Add exploration potential analysis
    if category == "forests_woods":
        popup_content += "🌲 <b>WOODED AREA</b><br>"
        popup_content += (
            "🎯 Exploration: EXCELLENT - Natural cover, trails, secluded spots<br>"
        )
    elif category == "nature_preserves":
        popup_content += "🦋 <b>NATURE PRESERVE</b><br>"
        popup_content += "🎯 Exploration: HIGH - Protected trails, wildlife viewing<br>"
    elif category == "state_county_parks":
        popup_content += "🏛️ <b>STATE/COUNTY PARK</b><br>"
        popup_content += "🎯 Exploration: EXCELLENT - Large area, multiple trails<br>"
    elif category == "major_parks":
        popup_content += "🏞️ <b>PUBLIC PARK</b><br>"
        popup_content += "🎯 Exploration: GOOD - Open to public, varied terrain<br>"

    # Add useful details
    relevant_tags = [
        "operator",
        "access",
        "opening_hours",
        "website",
        "description",
        "surface",
    ]
    for tag in relevant_tags:
        if tag in tags:
            popup_content += f"{tag.title()}: {tags[tag]}<br>"

    area_info = {"name": name, "category": category, "size": area_size, "tags": tags}

    # Add to map based on geometry type
    if item["type"] == "way" and "geometry" in item:
        coordinates = [[node["lat"], node["lon"]] for node in item["geometry"]]

        if len(coordinates) > 2:
            folium.Polygon(
                locations=coordinates,
                popup=popup_content,
                tooltip=f"{name} ({area_size})",
                color=colors["color"],
                weight=2,
                fill=True,
                fillColor=colors["fillColor"],
                fillOpacity=0.3,
            ).add_to(feature_group)

    elif item["type"] == "node":
        popup_content += f"📍 {item['lat']:.6f}, {item['lon']:.6f}"

        folium.Marker(
            location=[item["lat"], item["lon"]],
            popup=popup_content,
            tooltip=name,
            icon=folium.Icon(color=colors["color"], icon="tree", prefix="fa"),
        ).add_to(feature_group)

    return area_info


def main():
    print("🌳 LARGE PUBLIC AREAS SEARCH")
    print("🔍 Finding substantial parks, forests, and public lands for exploration")
    print("=" * 80)

    # The 4 precise corner coordinates
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    corner_labels = [
        "Day 18 Left (4-mile)",
        "Day 18 Right (4-mile)",
        "Day 15 cuts Day 18 (N)",
        "Day 15 cuts Day 18 (W)",
    ]

    # Calculate center and bounds
    center_lat = sum(coord[0] for coord in corners) / len(corners)
    center_lon = sum(coord[1] for coord in corners) / len(corners)

    lats = [corner[0] for corner in corners]
    lons = [corner[1] for corner in corners]

    south, north = min(lats) - 0.005, max(lats) + 0.005
    west, east = min(lons) - 0.005, max(lons) + 0.005
    bounds = (south, west, north, east)

    # Create enhanced map
    public_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # Add tile layers
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(public_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(public_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic View",
        overlay=False,
        control=True,
    ).add_to(public_map)

    # Add large public areas overlay
    public_map, area_details = add_public_areas_overlay(public_map, bounds)

    # Add corner markers
    colors = ["red", "blue", "green", "purple"]
    for i, (coord, label, color) in enumerate(zip(corners, corner_labels, colors)):
        folium.Marker(
            location=coord,
            popup=f"<b>Corner {i+1}: {label}</b><br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"Corner {i+1}: {label}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(public_map)

    # Add wedge outline
    quad_coords = [corners[0], corners[1], corners[2], corners[3], corners[0]]
    folium.Polygon(
        locations=quad_coords,
        color="red",
        weight=3,
        fill=False,
        popup="<b>🎯 SEARCH WEDGE</b><br>Large Public Areas Search<br>Perfect for exploration and outdoor activities",
        tooltip="Search Area Boundary",
    ).add_to(public_map)

    # Add layer control
    folium.LayerControl().add_to(public_map)

    # Save map
    output_file = "large_public_areas_wedge.html"
    public_map.save(output_file)

    print(f"\n🗺️ Large public areas map saved as: {output_file}")

    # Print summary of findings
    print(f"\n📊 SUMMARY OF LARGE PUBLIC AREAS:")
    total_found = 0
    for category, areas in area_details.items():
        if areas:
            total_found += len(areas)
            print(f"\n🌳 {category.replace('_', ' ').title()}: {len(areas)} found")
            for area in areas[:3]:  # Show first 3 of each type
                print(f"   📍 {area['name']} ({area['size']})")
            if len(areas) > 3:
                print(f"   ... and {len(areas) - 3} more")

    print(f"\n🎯 Total large public areas found: {total_found}")
    print(f"\n🌲 Perfect for:")
    print(f"   • Hiking and nature exploration")
    print(f"   • Wildlife observation")
    print(f"   • Photography and sightseeing")
    print(f"   • Outdoor recreation activities")
    print(f"   • Finding secluded spots for treasure hunting")

    return public_map


if __name__ == "__main__":
    main()
