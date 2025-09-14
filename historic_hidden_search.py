#!/usr/bin/env python3
"""
Enhanced Wedge Search with HISTORIC and HIDDEN LOCATION IDENTIFICATION

Specifically designed to find:
- Historic sites (like Sullivan Horse Track)
- Abandoned buildings and areas
- Ruins and archaeological sites
- Secluded areas near but off main paths
- Historic landmarks and monuments
- Old infrastructure and forgotten places
- Areas perfect for hiding items away from casual discovery
"""

import folium
import requests
from public_areas import PublicAreasOverlay


def get_historic_and_hidden_areas(bounds):
    """
    Get historic sites, abandoned areas, and secluded locations perfect for hidden items.

    Args:
        bounds: Tuple of (south, west, north, east) coordinates

    Returns:
        Dictionary with categorized historic and hidden locations
    """
    south, west, north, east = bounds

    # Comprehensive query for historic and abandoned features
    query = f"""
    [out:json][timeout:60];
    (
      // Historic sites and landmarks
      way["historic"]({south},{west},{north},{east});
      node["historic"]({south},{west},{north},{east});
      relation["historic"]({south},{west},{north},{east});
      
      // Abandoned and disused areas
      way["abandoned"]({south},{west},{north},{east});
      node["abandoned"]({south},{west},{north},{east});
      way["disused"]({south},{west},{north},{east});
      node["disused"]({south},{west},{north},{east});
      
      // Ruins and archaeological sites
      way["ruins"="yes"]({south},{west},{north},{east});
      node["ruins"="yes"]({south},{west},{north},{east});
      way["archaeological_site"]({south},{west},{north},{east});
      node["archaeological_site"]({south},{west},{north},{east});
      
      // Old infrastructure
      way["railway"="abandoned"]({south},{west},{north},{east});
      way["highway"="track"]["access"="private"]({south},{west},{north},{east});
      way["man_made"="ruins"]({south},{west},{north},{east});
      
      // Memorials and monuments (often secluded)
      way["historic"="memorial"]({south},{west},{north},{east});
      node["historic"="memorial"]({south},{west},{north},{east});
      way["historic"="monument"]({south},{west},{north},{east});
      node["historic"="monument"]({south},{west},{north},{east});
      
      // Cemeteries (historic and secluded areas)
      way["landuse"="cemetery"]({south},{west},{north},{east});
      way["amenity"="grave_yard"]({south},{west},{north},{east});
      
      // Quarries and mines (often abandoned/historic)
      way["landuse"="quarry"]({south},{west},{north},{east});
      way["man_made"="mine"]({south},{west},{north},{east});
      node["man_made"="mine_shaft"]({south},{west},{north},{east});
      
      // Old military sites
      way["military"="bunker"]({south},{west},{north},{east});
      node["military"="bunker"]({south},{west},{north},{east});
      way["historic"="fort"]({south},{west},{north},{east});
      
      // Specific search for horse/racing tracks
      way["leisure"="horse_riding"]({south},{west},{north},{east});
      way["sport"="horse_racing"]({south},{west},{north},{east});
      way["leisure"="track"]["sport"="horse_racing"]({south},{west},{north},{east});
      node["name"~"[Hh]orse.*[Tt]rack"]({south},{west},{north},{east});
      node["name"~"Sullivan"]({south},{west},{north},{east});
      
      // Old foundations and structures
      way["building"="ruins"]({south},{west},{north},{east});
      node["ruins"="building"]({south},{west},{north},{east});
      
      // Secluded natural features
      way["natural"="cave"]({south},{west},{north},{east});
      node["natural"="cave"]({south},{west},{north},{east});
      way["natural"="rock"]({south},{west},{north},{east});
      node["natural"="rock"]({south},{west},{north},{east});
    );
    out geom;
    """

    try:
        print("🔍 Searching for historic sites and hidden locations...")
        response = requests.post(
            "https://overpass-api.de/api/interpreter", data=query, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # Categorize the findings
        categories = {
            "historic_sites": [],
            "abandoned_areas": [],
            "ruins": [],
            "memorials": [],
            "cemeteries": [],
            "horse_tracks": [],
            "military": [],
            "mines_quarries": [],
            "caves_rocks": [],
            "old_infrastructure": [],
        }

        for element in data.get("elements", []):
            category = classify_historic_element(element)
            if category in categories:
                categories[category].append(element)

        return categories

    except Exception as e:
        print(f"⚠️ Error fetching historic data: {e}")
        return {
            k: []
            for k in [
                "historic_sites",
                "abandoned_areas",
                "ruins",
                "memorials",
                "cemeteries",
                "horse_tracks",
                "military",
                "mines_quarries",
                "caves_rocks",
                "old_infrastructure",
            ]
        }


def classify_historic_element(element):
    """Classify historic elements into hiding spot categories."""
    tags = element.get("tags", {})
    name = tags.get("name", "").lower()

    # Check for horse tracks specifically
    if (
        ("horse" in name and "track" in name)
        or tags.get("sport") == "horse_racing"
        or "sullivan" in name
    ):
        return "horse_tracks"

    # Historic sites
    elif tags.get("historic") in [
        "archaeological_site",
        "battlefield",
        "castle",
        "fort",
        "manor",
    ]:
        return "historic_sites"

    # Abandoned/disused
    elif "abandoned" in str(tags) or "disused" in str(tags):
        return "abandoned_areas"

    # Ruins
    elif (
        tags.get("ruins") == "yes"
        or tags.get("historic") == "ruins"
        or "ruins" in str(tags)
    ):
        return "ruins"

    # Memorials and monuments
    elif tags.get("historic") in ["memorial", "monument"]:
        return "memorials"

    # Cemeteries
    elif tags.get("landuse") == "cemetery" or tags.get("amenity") == "grave_yard":
        return "cemeteries"

    # Military sites
    elif tags.get("military") or tags.get("historic") == "fort":
        return "military"

    # Mines and quarries
    elif tags.get("landuse") == "quarry" or "mine" in str(tags):
        return "mines_quarries"

    # Natural hiding spots
    elif tags.get("natural") in ["cave", "rock"]:
        return "caves_rocks"

    # Old infrastructure
    elif tags.get("railway") == "abandoned" or (
        tags.get("highway") == "track" and tags.get("access") == "private"
    ):
        return "old_infrastructure"

    else:
        return "historic_sites"


def add_historic_overlay(map_obj, bounds):
    """Add historic and hidden location overlay to the map."""
    historic_data = get_historic_and_hidden_areas(bounds)

    # Color scheme for different types of hiding spots
    category_colors = {
        "horse_tracks": {
            "color": "darkred",
            "fillColor": "lightcoral",
            "icon": "horse",
            "name": "🐎 Horse Tracks & Racing",
        },
        "historic_sites": {
            "color": "purple",
            "fillColor": "lavender",
            "icon": "monument",
            "name": "🏛️ Historic Sites",
        },
        "abandoned_areas": {
            "color": "gray",
            "fillColor": "lightgray",
            "icon": "home",
            "name": "🏚️ Abandoned Areas",
        },
        "ruins": {
            "color": "brown",
            "fillColor": "tan",
            "icon": "university",
            "name": "🏺 Ruins & Archaeological",
        },
        "memorials": {
            "color": "black",
            "fillColor": "lightgray",
            "icon": "star",
            "name": "⭐ Memorials & Monuments",
        },
        "cemeteries": {
            "color": "darkgray",
            "fillColor": "whitesmoke",
            "icon": "cross",
            "name": "⛪ Cemeteries",
        },
        "military": {
            "color": "olive",
            "fillColor": "lightgreen",
            "icon": "shield",
            "name": "🛡️ Military Sites",
        },
        "mines_quarries": {
            "color": "orange",
            "fillColor": "lightyellow",
            "icon": "industry",
            "name": "⛏️ Mines & Quarries",
        },
        "caves_rocks": {
            "color": "darkblue",
            "fillColor": "lightblue",
            "icon": "mountain",
            "name": "🗿 Caves & Rock Formations",
        },
        "old_infrastructure": {
            "color": "darkgreen",
            "fillColor": "lightgreen",
            "icon": "road",
            "name": "🛤️ Old Infrastructure",
        },
    }

    total_historic = 0

    for category, items in historic_data.items():
        if not items:
            continue

        colors = category_colors.get(
            category,
            {
                "color": "gray",
                "fillColor": "lightgray",
                "icon": "map-marker",
                "name": category.title(),
            },
        )
        feature_group = folium.FeatureGroup(name=f"{colors['name']} ({len(items)})")

        for item in items:
            add_historic_item_to_map(feature_group, item, category, colors)
            total_historic += 1

        if len(items) > 0:
            feature_group.add_to(map_obj)

    print(f"🏛️ Added {total_historic} historic and hidden locations")
    return map_obj


def add_historic_item_to_map(feature_group, item, category, colors):
    """Add a historic item to the feature group with detailed information."""
    tags = item.get("tags", {})
    name = tags.get("name", f'Unnamed {category.replace("_", " ")}')

    # Create detailed popup for hiding spot analysis
    popup_content = f"<b>{name}</b><br>"
    popup_content += f"🎯 Type: {category.replace('_', ' ').title()}<br>"

    # Add hiding spot potential analysis
    if category == "horse_tracks":
        popup_content += "🐎 <b>HORSE TRACK FOUND!</b><br>"
        popup_content += "💡 Hiding potential: HIGH - Historic racing areas often have secluded spots<br>"
    elif category == "abandoned_areas":
        popup_content += "🏚️ <b>Abandoned/Disused Area</b><br>"
        popup_content += (
            "💡 Hiding potential: VERY HIGH - Away from regular foot traffic<br>"
        )
    elif category == "ruins":
        popup_content += "🏺 <b>Historic Ruins</b><br>"
        popup_content += (
            "💡 Hiding potential: HIGH - Old foundations, scattered stones<br>"
        )
    elif category == "caves_rocks":
        popup_content += "🗿 <b>Natural Formation</b><br>"
        popup_content += "💡 Hiding potential: EXCELLENT - Natural concealment<br>"

    # Add useful details
    relevant_tags = [
        "historic",
        "abandoned",
        "ruins",
        "access",
        "description",
        "start_date",
        "end_date",
    ]
    for tag in relevant_tags:
        if tag in tags:
            popup_content += f"{tag.title()}: {tags[tag]}<br>"

    # Add coordinates for reference
    if item["type"] == "node":
        popup_content += f"📍 {item['lat']:.6f}, {item['lon']:.6f}"

        # Add marker for point locations
        folium.Marker(
            location=[item["lat"], item["lon"]],
            popup=popup_content,
            tooltip=name,
            icon=folium.Icon(color=colors["color"], icon=colors["icon"], prefix="fa"),
        ).add_to(feature_group)

    elif item["type"] == "way" and "geometry" in item:
        coordinates = [[node["lat"], node["lon"]] for node in item["geometry"]]

        if len(coordinates) > 2 and coordinates[0] == coordinates[-1]:
            # Area/polygon
            folium.Polygon(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=colors["color"],
                weight=3,
                fill=True,
                fillColor=colors["fillColor"],
                fillOpacity=0.5,
            ).add_to(feature_group)
        else:
            # Path/line
            folium.PolyLine(
                locations=coordinates,
                popup=popup_content,
                tooltip=name,
                color=colors["color"],
                weight=4,
                opacity=0.8,
            ).add_to(feature_group)


def main():
    print("🎯 HISTORIC & HIDDEN LOCATION SEARCH")
    print("🔍 Searching for Sullivan Horse Track and other secluded hiding spots")
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
    search_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add tile layers
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

    # Add historic and hidden location overlay
    search_map = add_historic_overlay(search_map, bounds)

    # Add regular public areas for context
    try:
        overlay = PublicAreasOverlay()
        comprehensive_types = ["park", "hiking", "recreation", "water"]
        public_areas = overlay.get_public_areas(bounds, comprehensive_types)

        for area_type, areas in public_areas.items():
            if areas:
                colors = {
                    "park": "green",
                    "hiking": "brown",
                    "recreation": "blue",
                    "water": "cyan",
                }.get(area_type, "gray")
                feature_group = folium.FeatureGroup(
                    name=f"Context: {area_type.title()} ({len(areas)})"
                )

                for area in areas:
                    if area["type"] == "way" and "geometry" in area:
                        coords = [[n["lat"], n["lon"]] for n in area["geometry"]]
                        if len(coords) > 1:
                            folium.PolyLine(
                                locations=coords, color=colors, weight=2, opacity=0.4
                            ).add_to(feature_group)

                feature_group.add_to(search_map)

    except Exception as e:
        print(f"⚠️ Could not load context areas: {e}")

    # Add corner markers
    colors = ["red", "blue", "green", "purple"]
    for i, (coord, label, color) in enumerate(zip(corners, corner_labels, colors)):
        folium.Marker(
            location=coord,
            popup=f"<b>Corner {i+1}: {label}</b><br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"Corner {i+1}: {label}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(search_map)

    # Add wedge outline
    quad_coords = [corners[0], corners[1], corners[2], corners[3], corners[0]]
    folium.Polygon(
        locations=quad_coords,
        color="orange",
        weight=4,
        fill=False,
        popup="<b>🎯 SEARCH WEDGE</b><br>Historic & Hidden Location Search<br>Perfect for items hidden off main paths",
        tooltip="Search Area Boundary",
    ).add_to(search_map)

    # Add layer control
    folium.LayerControl().add_to(search_map)

    # Save map
    output_file = "historic_hidden_locations_wedge.html"
    search_map.save(output_file)

    print(f"\n🗺️ Historic and hidden locations map saved as: {output_file}")
    print(f"\n🎯 Perfect hiding spots for items that are:")
    print(f"   📍 Accessible but off main paths")
    print(f"   🌲 Hidden in wooded or secluded areas")
    print(f"   🏛️ Near historic sites that aren't heavily visited")
    print(f"   🏚️ In abandoned or forgotten areas")
    print(f"   🗿 Around natural features providing concealment")

    print(f"\n🐎 Specifically searching for:")
    print(f"   • Sullivan Horse Track (and other racing facilities)")
    print(f"   • Abandoned buildings and infrastructure")
    print(f"   • Historic ruins and archaeological sites")
    print(f"   • Old military installations")
    print(f"   • Forgotten cemeteries and memorials")
    print(f"   • Natural caves and rock formations")

    return search_map


if __name__ == "__main__":
    main()
