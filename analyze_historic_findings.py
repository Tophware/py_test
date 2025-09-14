#!/usr/bin/env python3
"""
HISTORIC SITES ANALYSIS
Show detailed information about historic and hidden locations found within the search wedge
"""

import requests
from public_areas import PublicAreasOverlay


def analyze_historic_findings():
    """Analyze what historic sites were found in the search area."""

    # The 4 precise corner coordinates
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    # Calculate bounds
    lats = [corner[0] for corner in corners]
    lons = [corner[1] for corner in corners]

    south, north = min(lats) - 0.005, max(lats) + 0.005
    west, east = min(lons) - 0.005, max(lons) + 0.005
    bounds = (south, west, north, east)

    print("🔍 DETAILED HISTORIC SITE ANALYSIS")
    print("=" * 60)
    print(f"📍 Search area bounds:")
    print(f"   North: {north:.6f}")
    print(f"   South: {south:.6f}")
    print(f"   East: {east:.6f}")
    print(f"   West: {west:.6f}")
    print()

    # Specific query to find detailed information about historic sites
    query = f"""
    [out:json][timeout:60];
    (
      // Historic sites and landmarks with detailed info
      way["historic"]({south},{west},{north},{east});
      node["historic"]({south},{west},{north},{east});
      relation["historic"]({south},{west},{north},{east});
      
      // Horse tracks specifically
      way["leisure"="horse_riding"]({south},{west},{north},{east});
      way["sport"="horse_racing"]({south},{west},{north},{east});
      way["leisure"="track"]["sport"="horse_racing"]({south},{west},{north},{east});
      node["name"~"[Hh]orse.*[Tt]rack",i]({south},{west},{north},{east});
      node["name"~"Sullivan",i]({south},{west},{north},{east});
      way["name"~"Sullivan",i]({south},{west},{north},{east});
      
      // Abandoned and ruins
      way["abandoned"]({south},{west},{north},{east});
      node["abandoned"]({south},{west},{north},{east});
      way["ruins"="yes"]({south},{west},{north},{east});
      node["ruins"="yes"]({south},{west},{north},{east});
      
      // Cemeteries
      way["landuse"="cemetery"]({south},{west},{north},{east});
      way["amenity"="grave_yard"]({south},{west},{north},{east});
      
      // Military sites
      way["military"]({south},{west},{north},{east});
      node["military"]({south},{west},{north},{east});
      
      // Natural features for hiding
      way["natural"="cave"]({south},{west},{north},{east});
      node["natural"="cave"]({south},{west},{north},{east});
      way["natural"="rock"]({south},{west},{north},{east});
      
      // Quarries and mines
      way["landuse"="quarry"]({south},{west},{north},{east});
      way["man_made"="mine"]({south},{west},{north},{east});
    );
    out geom;
    """

    try:
        print("🔍 Querying OpenStreetMap for historic data...")
        response = requests.post(
            "https://overpass-api.de/api/interpreter", data=query, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        elements = data.get("elements", [])
        print(f"📊 Found {len(elements)} total elements")
        print()

        # Categorize findings
        categories = {
            "Sullivan/Horse Tracks": [],
            "Historic Sites": [],
            "Cemeteries": [],
            "Military Sites": [],
            "Abandoned/Ruins": [],
            "Natural Features": [],
            "Quarries/Mines": [],
            "Other": [],
        }

        for element in elements:
            tags = element.get("tags", {})
            name = tags.get("name", "Unnamed")

            # Check for Sullivan or horse tracks
            if (
                "sullivan" in name.lower()
                or "horse" in name.lower()
                or tags.get("sport") == "horse_racing"
                or tags.get("leisure") == "horse_riding"
            ):
                categories["Sullivan/Horse Tracks"].append(element)

            # Historic sites
            elif tags.get("historic"):
                categories["Historic Sites"].append(element)

            # Cemeteries
            elif (
                tags.get("landuse") == "cemetery" or tags.get("amenity") == "grave_yard"
            ):
                categories["Cemeteries"].append(element)

            # Military
            elif tags.get("military"):
                categories["Military Sites"].append(element)

            # Abandoned/ruins
            elif "abandoned" in str(tags) or tags.get("ruins") == "yes":
                categories["Abandoned/Ruins"].append(element)

            # Natural features
            elif tags.get("natural") in ["cave", "rock"]:
                categories["Natural Features"].append(element)

            # Quarries/mines
            elif tags.get("landuse") == "quarry" or "mine" in str(tags):
                categories["Quarries/Mines"].append(element)

            else:
                categories["Other"].append(element)

        # Display findings
        for category, items in categories.items():
            if items:
                print(f"🎯 {category.upper()} ({len(items)} found)")
                print("-" * (len(category) + 15))

                for item in items:
                    tags = item.get("tags", {})
                    name = tags.get("name", "Unnamed location")

                    print(f"   📍 {name}")

                    # Show location
                    if item["type"] == "node":
                        lat, lon = item["lat"], item["lon"]
                        print(f"      Location: {lat:.6f}, {lon:.6f}")

                    # Show relevant tags
                    relevant_tags = [
                        "historic",
                        "sport",
                        "leisure",
                        "landuse",
                        "amenity",
                        "military",
                        "natural",
                        "abandoned",
                        "ruins",
                        "access",
                        "description",
                    ]
                    for tag in relevant_tags:
                        if tag in tags:
                            print(f"      {tag.title()}: {tags[tag]}")

                    # Hiding potential analysis
                    if category == "Sullivan/Horse Tracks":
                        print(
                            f"      🎯 HIDING POTENTIAL: VERY HIGH - Historic horse track area!"
                        )
                        print(
                            f"      💡 Look for: Old stables, grandstand ruins, fence posts"
                        )
                    elif category == "Cemeteries":
                        print(
                            f"      🎯 HIDING POTENTIAL: HIGH - Secluded, old sections"
                        )
                        print(
                            f"      💡 Look for: Old trees, forgotten corners, maintenance areas"
                        )
                    elif category == "Abandoned/Ruins":
                        print(f"      🎯 HIDING POTENTIAL: EXCELLENT - Forgotten areas")
                        print(
                            f"      💡 Look for: Foundation stones, overgrown structures"
                        )
                    elif category == "Historic Sites":
                        print(
                            f"      🎯 HIDING POTENTIAL: GOOD - Less visited historic areas"
                        )
                        print(
                            f"      💡 Look for: Edges of site, interpretive trail offshoots"
                        )

                    print()

                print()

        # Special Sullivan search
        print("🐎 SPECIAL SULLIVAN HORSE TRACK SEARCH")
        print("=" * 50)
        sullivan_query = f"""
        [out:json][timeout:30];
        (
          node["name"~"Sullivan",i]({south},{west},{north},{east});
          way["name"~"Sullivan",i]({south},{west},{north},{east});
          relation["name"~"Sullivan",i]({south},{west},{north},{east});
        );
        out geom;
        """

        sullivan_response = requests.post(
            "https://overpass-api.de/api/interpreter", data=sullivan_query, timeout=30
        )
        sullivan_data = sullivan_response.json()
        sullivan_elements = sullivan_data.get("elements", [])

        if sullivan_elements:
            print(
                f"🎯 Found {len(sullivan_elements)} locations with 'Sullivan' in the name!"
            )
            for element in sullivan_elements:
                tags = element.get("tags", {})
                name = tags.get("name", "Unnamed Sullivan location")
                print(f"   📍 {name}")
                if element["type"] == "node":
                    print(
                        f"      📍 Location: {element['lat']:.6f}, {element['lon']:.6f}"
                    )
                for key, value in tags.items():
                    if key != "name":
                        print(f"      {key}: {value}")
                print()
        else:
            print("❌ No locations with 'Sullivan' found in the immediate search area")
            print("💡 The Sullivan Horse Track might be:")
            print("   • Just outside the search wedge boundaries")
            print("   • Named differently in OpenStreetMap")
            print("   • Not mapped in OSM (common for abandoned tracks)")
            print("   • Mapped under a different category")

        print()
        print("🗺️ Map saved as: historic_hidden_locations_wedge.html")
        print(
            "📂 Open this file in a web browser to see all locations marked on the map"
        )

    except Exception as e:
        print(f"❌ Error analyzing historic data: {e}")


if __name__ == "__main__":
    analyze_historic_findings()
