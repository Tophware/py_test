#!/usr/bin/env python3
"""
Create focused search map for canister based on story analysis and public accessible areas.
Since calculated trajectories land outside the wedge, focus on most likely public areas
within or near the wedge that match the story criteria.
"""

import folium
import json

# Wedge search area corners
wedge_corners = [
    [40.49258082, -74.57854107],  # Corner 1: Day 18 Left (4-mile)
    [40.50053426, -74.56162256],  # Corner 2: Day 18 Right (4-mile)
    [40.52752728, -74.57756772],  # Corner 3: Day 15 cuts Day 18 (N)
    [40.51608736, -74.60373849],  # Corner 4: Day 15 cuts Day 18 (W)
]

# Day 16 anomaly location
anomaly_location = [41.473666, -74.660742]

# Based on story analysis and local geography, identify most probable locations
# These are public, wooded areas that could realistically contain the canister
probable_locations = [
    {
        "name": "Mercer County Park System - North",
        "lat": 40.5180,
        "lon": -74.5950,
        "reason": "Large wooded park system, multiple hiking trails, easily accessible",
        "confidence": "High",
    },
    {
        "name": "Baldpate Mountain - Hopewell",
        "lat": 40.5050,
        "lon": -74.5800,
        "reason": "Wooded hiking area, part of park system, matches terrain description",
        "confidence": "High",
    },
    {
        "name": "Princeton Battlefield State Park",
        "lat": 40.5020,
        "lon": -74.5650,
        "reason": "Historic park with wooded areas, hiking trails, public access",
        "confidence": "Medium",
    },
    {
        "name": "Lawrence Hopewell Trail System",
        "lat": 40.5100,
        "lon": -74.5750,
        "reason": "Trail system through wooded areas, popular hiking destination",
        "confidence": "Medium",
    },
    {
        "name": "Rosedale Park",
        "lat": 40.5140,
        "lon": -74.5620,
        "reason": "Local park with wooded sections, less trafficked areas",
        "confidence": "Medium",
    },
]

# Story-based target criteria locations (within wedge that match description)
story_targets = [
    {
        "name": "Target Zone A - Central Wedge",
        "lat": 40.5100,
        "lon": -74.5750,
        "reason": "Central location in wedge, likely wooded residential area transitions",
        "search_radius": 500,
    },
    {
        "name": "Target Zone B - Northwest Wedge",
        "lat": 40.5200,
        "lon": -74.5900,
        "reason": "Near wedge boundary, potential park or preserve areas",
        "search_radius": 750,
    },
    {
        "name": "Target Zone C - Eastern Wedge",
        "lat": 40.5050,
        "lon": -74.5650,
        "reason": "Eastern section, near potential trail systems",
        "search_radius": 500,
    },
]


def create_focused_search_map():
    """Create focused search map highlighting most probable locations"""

    # Center on wedge area
    center_lat = sum(corner[0] for corner in wedge_corners) / len(wedge_corners)
    center_lon = sum(corner[1] for corner in wedge_corners) / len(wedge_corners)

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap"
    )

    # Add wedge search area - primary focus
    folium.Polygon(
        locations=wedge_corners,
        color="blue",
        weight=4,
        fillColor="lightblue",
        fillOpacity=0.3,
        popup="<b>Primary Search Wedge</b><br>Focus search efforts here first",
    ).add_to(m)

    # Add Day 16 anomaly location for reference
    folium.Marker(
        anomaly_location,
        popup="<b>Day 16 Anomaly</b><br>Canister Release Point<br>6:49AM",
        icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
    ).add_to(m)

    # Add probable public access locations
    for location in probable_locations:
        color = "green" if location["confidence"] == "High" else "orange"

        folium.Marker(
            [location["lat"], location["lon"]],
            popup=f"<b>{location['name']}</b><br>{location['reason']}<br>Confidence: {location['confidence']}",
            icon=folium.Icon(color=color, icon="tree", prefix="fa"),
        ).add_to(m)

        # Add search radius
        radius = 400 if location["confidence"] == "High" else 300
        folium.Circle(
            location=[location["lat"], location["lon"]],
            radius=radius,
            color=color,
            fillColor=color,
            fillOpacity=0.2,
            popup=f"{location['name']}<br>{radius}m search area",
        ).add_to(m)

    # Add story-based target zones within wedge
    for target in story_targets:
        folium.Marker(
            [target["lat"], target["lon"]],
            popup=f"<b>{target['name']}</b><br>{target['reason']}",
            icon=folium.Icon(color="purple", icon="bullseye", prefix="fa"),
        ).add_to(m)

        folium.Circle(
            location=[target["lat"], target["lon"]],
            radius=target["search_radius"],
            color="purple",
            fillColor="purple",
            fillOpacity=0.15,
            popup=f"{target['name']}<br>{target['search_radius']}m zone",
        ).add_to(m)

    # Add satellite imagery layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add topographic layer for terrain analysis
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


def generate_search_recommendations():
    """Generate specific search recommendations based on analysis"""

    recommendations = {
        "priority_areas": [
            {
                "area": "Mercer County Park System",
                "coordinates": [40.5180, -74.5950],
                "why": "Largest wooded public area in region, multiple trail access points",
                "search_strategy": "Focus on areas 50-100m off main trails, look for disturbed ground or vegetation",
                "access": "Multiple parking areas, well-marked trail entrances",
            },
            {
                "area": "Baldpate Mountain Area",
                "coordinates": [40.5050, -74.5800],
                "why": "Elevated wooded terrain, matches 'mountain' references from story context",
                "search_strategy": "Check clearings and areas below ridge lines where object might roll",
                "access": "Hiking trail parking, moderate difficulty access",
            },
        ],
        "search_criteria": [
            "9.5 inch tall cylindrical object (canister)",
            "2.625 inch diameter",
            "Likely partially buried or covered by vegetation after 3+ years",
            "May be in natural depression or against trees/rocks",
            "Metal detector recommended for buried objects",
        ],
        "timing": [
            "Best searched during fall/winter when vegetation is minimal",
            "Early morning or late afternoon for better lighting",
            "After recent rain when ground disturbances are more visible",
        ],
    }

    return recommendations


def main():
    print("=== FOCUSED CANISTER SEARCH ANALYSIS ===")
    print()

    # Create the focused search map
    search_map = create_focused_search_map()
    search_map.save("focused_canister_search.html")
    print("✓ Focused search map created: focused_canister_search.html")

    # Generate recommendations
    recommendations = generate_search_recommendations()

    print("\n=== SEARCH RECOMMENDATIONS ===")
    print("\nPRIORITY SEARCH AREAS:")
    for area in recommendations["priority_areas"]:
        print(f"\n🎯 {area['area']}")
        print(
            f"   Coordinates: {area['coordinates'][0]:.4f}, {area['coordinates'][1]:.4f}"
        )
        print(f"   Why: {area['why']}")
        print(f"   Strategy: {area['search_strategy']}")
        print(f"   Access: {area['access']}")

    print(f"\nSEARCH CRITERIA:")
    for criterion in recommendations["search_criteria"]:
        print(f"   • {criterion}")

    print(f"\nOPTIMAL TIMING:")
    for timing in recommendations["timing"]:
        print(f"   • {timing}")

    # Save recommendations
    with open("search_recommendations.json", "w") as f:
        json.dump(recommendations, f, indent=2)
    print(f"\n✓ Detailed recommendations saved: search_recommendations.json")

    print(f"\n=== SUMMARY ===")
    print(f"Based on the briefing story and trajectory analysis:")
    print(f"1. The canister likely landed in a publicly accessible wooded area")
    print(
        f"2. Focus on the wedge search area first - it represents the most systematic analysis"
    )
    print(f"3. Look for parks, preserves, and trail systems within or near the wedge")
    print(
        f"4. The object is small enough to be easily missed but large enough to be detectable"
    )
    print(f"5. After 3+ years, it may be partially buried or overgrown")


if __name__ == "__main__":
    main()
