#!/usr/bin/env python3
"""
Quick summary of public areas found within the Day 15/Day 18 wedge search area.
"""

from public_areas import PublicAreasOverlay


def analyze_wedge_activities():
    """Analyze what specific outdoor activities are available in the wedge."""

    # The 4 precise corner coordinates of your wedge
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    print("🔍 ANALYZING PUBLIC AREAS IN YOUR SEARCH WEDGE")
    print("=" * 60)

    # Calculate bounds
    lats = [corner[0] for corner in corners]
    lons = [corner[1] for corner in corners]

    south, north = min(lats) - 0.005, max(lats) + 0.005
    west, east = min(lons) - 0.005, max(lons) + 0.005
    bounds = (south, west, north, east)

    # Get public areas data
    overlay = PublicAreasOverlay()
    comprehensive_types = [
        "park",
        "hiking",
        "recreation",
        "water",
        "tourism",
        "education",
    ]
    public_areas = overlay.get_public_areas(bounds, comprehensive_types)

    total_areas = 0
    activity_details = {}

    for area_type, areas in public_areas.items():
        if not areas:
            continue

        # Analyze specific activities within each area type
        activities = analyze_activity_type(areas, area_type)
        activity_details[area_type] = activities
        total_areas += len(areas)

    print(f"\n📊 SUMMARY: Found {total_areas} public areas in your 2.76 sq mile wedge!")
    print("\n🎯 SPECIFIC OUTDOOR ACTIVITIES IDENTIFIED:")
    print("-" * 50)

    for area_type, activities in activity_details.items():
        if activities["count"] > 0:
            print(
                f"\n{activities['icon']} {area_type.upper()} ({activities['count']} areas)"
            )
            for activity in activities["specific"]:
                print(f"    • {activity}")

    print(
        f"\n🗺️  This data is now overlaid on your enhanced_wedge_search_area.html map!"
    )
    print(
        f"    Each area type has its own color-coded layer that you can toggle on/off."
    )

    return activity_details


def analyze_activity_type(areas, area_type):
    """Analyze specific activities within an area type."""

    activity_info = {
        "park": {
            "icon": "🌳",
            "specific": [
                "Parks",
                "Gardens",
                "Nature reserves",
                "Forests",
                "Green spaces",
                "Recreation grounds",
            ],
            "trails": ["Walking paths in parks", "Nature trails"],
        },
        "hiking": {
            "icon": "🥾",
            "specific": [
                "Hiking trails",
                "Walking paths",
                "Footways",
                "Nature paths",
                "Track routes",
                "Bridleways",
            ],
            "trails": ["All trail types for walking/hiking"],
        },
        "recreation": {
            "icon": "⚽",
            "specific": [
                "Sports centers",
                "Playgrounds",
                "Golf courses",
                "Swimming pools",
                "Fitness centers",
                "Community centers",
                "Sports pitches",
            ],
            "trails": ["Fitness trails", "Running tracks", "Sports facility paths"],
        },
        "water": {
            "icon": "💧",
            "specific": ["Lakes", "Rivers", "Marinas", "Beaches", "Swimming areas"],
            "trails": ["Waterfront paths", "Riverside trails"],
        },
        "tourism": {
            "icon": "🏛️",
            "specific": [
                "Tourist attractions",
                "Viewpoints",
                "Picnic sites",
                "Campsites",
                "Scenic areas",
            ],
            "trails": ["Scenic walking routes", "Tourist trails"],
        },
        "education": {
            "icon": "🎓",
            "specific": [
                "Universities",
                "Schools",
                "Libraries",
                "Educational facilities",
            ],
            "trails": ["Campus paths", "Educational trails"],
        },
    }

    info = activity_info.get(
        area_type, {"icon": "📍", "specific": [area_type.title()], "trails": []}
    )

    # Count specific activity types by analyzing tags
    specific_activities = set()

    for area in areas:
        tags = area.get("tags", {})

        # Add specific activity based on tags
        if area_type == "hiking":
            if tags.get("highway") == "path":
                specific_activities.add("🥾 Hiking paths")
            if tags.get("highway") == "footway":
                specific_activities.add("🚶 Walking footways")
            if tags.get("highway") == "track":
                specific_activities.add("🚶 Track routes")
            if tags.get("foot") == "designated":
                specific_activities.add("🚶 Designated walking paths")
        elif area_type == "recreation":
            if tags.get("leisure") == "playground":
                specific_activities.add("🎪 Playgrounds")
            if tags.get("leisure") == "sports_centre":
                specific_activities.add("🏃 Sports centers")
            if tags.get("leisure") == "pitch":
                specific_activities.add("⚽ Sports fields/pitches")
            if tags.get("leisure") == "swimming_pool":
                specific_activities.add("🏊 Swimming pools")
            if tags.get("leisure") == "golf_course":
                specific_activities.add("⛳ Golf courses")
        elif area_type == "park":
            if tags.get("leisure") == "park":
                specific_activities.add("🌳 Public parks")
            if tags.get("leisure") == "garden":
                specific_activities.add("🌺 Gardens")
            if tags.get("landuse") == "forest":
                specific_activities.add("🌲 Forest areas")

    # Include biking/cycling analysis
    biking_activities = set()
    for area in areas:
        tags = area.get("tags", {})
        if (
            tags.get("highway") == "cycleway"
            or "cycleway" in tags
            or tags.get("bicycle") in ["designated", "yes"]
        ):
            biking_activities.add("🚴 Biking/cycling paths")

    if biking_activities:
        specific_activities.update(biking_activities)

    # Add running/fitness specific
    fitness_activities = set()
    for area in areas:
        tags = area.get("tags", {})
        if tags.get("sport") == "running":
            fitness_activities.add("🏃 Running tracks")
        if tags.get("leisure") == "fitness_centre":
            fitness_activities.add("💪 Fitness centers")
        if tags.get("leisure") == "fitness_station":
            fitness_activities.add("💪 Outdoor fitness stations")

    if fitness_activities:
        specific_activities.update(fitness_activities)

    return {
        "icon": info["icon"],
        "count": len(areas),
        "specific": (
            list(specific_activities) if specific_activities else info["specific"][:3]
        ),
    }


if __name__ == "__main__":
    analyze_wedge_activities()
