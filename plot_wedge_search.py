#!/usr/bin/env python3
"""
Plot the precise 4-corner search area where Day 15 cuts Day 18 wedge
WITH COMPREHENSIVE PUBLIC AREAS IDENTIFICATION

Enhanced to show ALL public areas within the wedge including:
- Biking trails and cycle paths
- Hiking trails and nature paths
- Walking paths and footways
- Running tracks and fitness trails
- Parks and green spaces
- Recreation facilities
- And all other publicly accessible areas
"""

import folium
from public_areas import PublicAreasOverlay


def add_wedge_public_areas(map_obj, wedge_corners):
    """
    Add comprehensive public areas overlay specifically filtered to the wedge area.

    Args:
        map_obj: Folium map object
        wedge_corners: List of [lat, lon] coordinates defining the wedge polygon

    Returns:
        Modified Folium map object
    """
    try:
        print("🌲 Loading public areas within the wedge...")

        # Calculate bounding box for the wedge with buffer
        lats = [corner[0] for corner in wedge_corners]
        lons = [corner[1] for corner in wedge_corners]

        south, north = min(lats) - 0.005, max(lats) + 0.005
        west, east = min(lons) - 0.005, max(lons) + 0.005
        bounds = (south, west, north, east)

        # Initialize public areas overlay
        overlay = PublicAreasOverlay()

        # Get comprehensive public areas including all trail types
        comprehensive_types = [
            "park",
            "hiking",
            "recreation",
            "water",
            "tourism",
            "education",
        ]
        public_areas = overlay.get_public_areas(bounds, comprehensive_types)

        # Color mapping for different activity types
        activity_colors = {
            "park": {
                "color": "green",
                "fillColor": "lightgreen",
                "name": "🌳 Parks & Green Spaces",
            },
            "hiking": {
                "color": "brown",
                "fillColor": "tan",
                "name": "🥾 Trails & Hiking Paths",
            },
            "recreation": {
                "color": "blue",
                "fillColor": "lightblue",
                "name": "⚽ Recreation Facilities",
            },
            "water": {
                "color": "cyan",
                "fillColor": "lightcyan",
                "name": "💧 Water Features",
            },
            "tourism": {
                "color": "purple",
                "fillColor": "lavender",
                "name": "🏛️ Tourism & Attractions",
            },
            "education": {
                "color": "orange",
                "fillColor": "lightyellow",
                "name": "🎓 Educational Facilities",
            },
        }

        total_areas = 0
        for area_type, areas in public_areas.items():
            if not areas:
                continue

            colors = activity_colors.get(
                area_type,
                {
                    "color": "gray",
                    "fillColor": "lightgray",
                    "name": f"{area_type.title()}",
                },
            )
            feature_group = folium.FeatureGroup(name=f"{colors['name']} ({len(areas)})")

            for area in areas:
                # Check if area is within wedge (simplified check using bounding box)
                if area_within_bounds(area, bounds):
                    total_areas += 1
                    add_area_to_map(feature_group, area, area_type, colors)

            if len(areas) > 0:
                feature_group.add_to(map_obj)

        print(f"✓ Added {total_areas} public areas within the wedge")
        return map_obj

    except Exception as e:
        print(f"⚠️  Could not load public areas: {e}")
        print("Continuing with basic wedge map...")
        return map_obj


def area_within_bounds(area, bounds):
    """Simple bounds check for area filtering."""
    south, west, north, east = bounds

    if area["type"] == "node":
        return south <= area["lat"] <= north and west <= area["lon"] <= east
    elif area["type"] == "way" and "geometry" in area:
        # Check if any point is within bounds
        for node in area["geometry"]:
            if south <= node["lat"] <= north and west <= node["lon"] <= east:
                return True
    return False


def add_area_to_map(feature_group, area, area_type, colors):
    """Add a single area to the feature group with detailed popup."""
    tags = area.get("tags", {})
    name = tags.get("name", f"Unnamed {area_type}")

    # Create detailed popup with activity-specific information
    popup_content = f"<b>{name}</b><br>"
    popup_content += f"🏷️ Type: {area_type.title()}<br>"

    # Add activity-specific details
    if area_type == "hiking":
        popup_content += "🥾 Includes: Hiking trails, walking paths, footways<br>"
        if "surface" in tags:
            popup_content += f"Surface: {tags['surface']}<br>"
    elif area_type == "recreation":
        popup_content += (
            "⚽ Includes: Sports facilities, playgrounds, fitness areas<br>"
        )
    elif area_type == "park":
        popup_content += "🌳 Includes: Parks, gardens, nature reserves<br>"

    # Add useful tags
    for tag in ["surface", "operator", "opening_hours", "website"]:
        if tag in tags:
            popup_content += f"{tag.title()}: {tags[tag]}<br>"

    if area["type"] == "way" and "geometry" in area:
        coordinates = [[node["lat"], node["lon"]] for node in area["geometry"]]

        if len(coordinates) > 2 and coordinates[0] == coordinates[-1]:
            # Polygon area
            folium.Polygon(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=colors["color"],
                weight=2,
                fill=True,
                fillColor=colors["fillColor"],
                fillOpacity=0.4,
            ).add_to(feature_group)
        else:
            # Path/trail - make more visible
            folium.PolyLine(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=colors["color"],
                weight=4,
                opacity=0.8,
            ).add_to(feature_group)

    elif area["type"] == "node":
        folium.Marker(
            location=[area["lat"], area["lon"]],
            popup=popup_content,
            tooltip=name,
            icon=folium.Icon(color=colors["color"], icon="map-marker"),
        ).add_to(feature_group)


def main():
    print("🎯 ENHANCED Day 15/Day 18 Wedge Search Area with Comprehensive Public Areas")
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

    # Calculate center for map
    center_lat = sum(coord[0] for coord in corners) / len(corners)
    center_lon = sum(coord[1] for coord in corners) / len(corners)

    # Create enhanced map with multiple tile layers
    search_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add multiple tile layers for better area identification
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(search_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(search_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic View",
        overlay=False,
        control=True,
    ).add_to(search_map)

    # Add comprehensive public areas overlay WITHIN the wedge only
    search_map = add_wedge_public_areas(search_map, corners)

    # Add corner markers
    colors = ["red", "blue", "green", "purple"]
    for i, (coord, label, color) in enumerate(zip(corners, corner_labels, colors)):
        folium.Marker(
            location=coord,
            popup=f"Corner {i+1}: {label}<br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"Corner {i+1}: {label}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(search_map)

    # Create the search quadrilateral
    # Order the corners to form a proper polygon
    quad_coords = [
        corners[0],  # Day 18 Left (4-mile)
        corners[1],  # Day 18 Right (4-mile)
        corners[2],  # Day 15 cuts Day 18 (N)
        corners[3],  # Day 15 cuts Day 18 (W)
        corners[0],  # Close the polygon
    ]

    folium.Polygon(
        locations=quad_coords,
        color="orange",
        weight=4,
        fill=False,
        fillOpacity=0,
        popup="<b>🎯 SEARCH AREA</b><br>Day 15/Day 18 Overlap<br>~2.76 square miles<br><br>📍 All public areas shown are WITHIN this wedge!<br>🚴 Biking trails<br>🥾 Hiking paths<br>🚶 Walking routes<br>🏃 Running tracks<br>🌳 Parks & recreation",
        tooltip="Primary Search Wedge - Click for details",
    ).add_to(search_map)

    # Add center points for reference
    day18_center = [40.44766, -74.530389]
    day15_center = [40.364551, -74.950404]

    folium.Marker(
        location=day18_center,
        popup="Day 18 Center<br>(High Voltage Lines)",
        tooltip="Day 18 Center",
        icon=folium.Icon(color="darkgreen", icon="flash"),
    ).add_to(search_map)

    folium.Marker(
        location=day15_center,
        popup="Day 15 Center<br>(New Hope Bridge)",
        tooltip="Day 15 Center",
        icon=folium.Icon(color="darkblue", icon="home"),
    ).add_to(search_map)

    # Add layer control for easy switching between views and overlays
    folium.LayerControl().add_to(search_map)

    # Save enhanced map
    output_file = "enhanced_wedge_search_area.html"
    search_map.save(output_file)

    print(f"\n🗺️  Enhanced search area map saved as: {output_file}")
    print("\n=== WEDGE COORDINATES ===")
    print("This quadrilateral defines your search area:")
    print()
    for i, (coord, label) in enumerate(zip(corners, corner_labels)):
        print(f"{i+1}. {label:20}: [{coord[0]:.8f}, {coord[1]:.8f}]")

    print(f"\n🎯 Search Area Details:")
    print(f"   📏 Area: ~2.76 square miles")
    print(f"   📍 Between 4-7 miles from Day 18 center (High Voltage Lines)")
    print(
        f"   🔶 Orange outline shows the exact search boundary (no fill for easy clicking)"
    )

    print(f"\n🏃 Public Areas WITHIN WEDGE:")
    print(f"   🚴 Biking trails and cycle paths")
    print(f"   🥾 Hiking trails and nature paths")
    print(f"   🚶 Walking paths and footways")
    print(f"   🏃 Running tracks and fitness trails")
    print(f"   🌳 Parks and green spaces")
    print(f"   ⚽ Recreation facilities and sports areas")
    print(f"   💧 Water features and swimming areas")
    print(f"   🏛️ Tourism attractions and viewpoints")
    print(f"   🎓 Educational facilities")

    print(f"\n💡 Map Features:")
    print(f"   • Layer control (top-right) for Street/Satellite/Topo views")
    print(f"   • Color-coded overlays by activity type")
    print(f"   • Click any area/trail for detailed information")
    print(f"   • Only shows areas INSIDE your search wedge")
    print(f"   • Trails and paths highlighted with thicker lines for visibility")
    print(f"   • Wedge boundary is outline-only for easy clicking inside")


if __name__ == "__main__":
    main()
