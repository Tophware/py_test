"""
Public Areas Utility Functions

Helper functions to easily enable/disable and configure public areas on your maps.
"""

from main import create_map_with_all_datasets, PUBLIC_AREAS_CONFIG
import os


def create_map_with_public_areas(area_types=None, padding_miles=5):
    """
    Create your main map with public areas overlay enabled.

    Args:
        area_types: List of area types to display. Options:
                   'park', 'hiking', 'recreation', 'beach', 'water', 'tourism', 'education'
        padding_miles: Extra padding around sectors when fetching public areas

    Returns:
        Folium map object
    """
    # Configure public areas
    PUBLIC_AREAS_CONFIG["enabled"] = True
    if area_types:
        PUBLIC_AREAS_CONFIG["area_types"] = area_types
    PUBLIC_AREAS_CONFIG["padding_miles"] = padding_miles

    # Create the map
    return create_map_with_all_datasets()


def create_map_without_public_areas():
    """
    Create your main map with public areas overlay disabled.

    Returns:
        Folium map object
    """
    # Disable public areas
    PUBLIC_AREAS_CONFIG["enabled"] = False

    # Create the map
    return create_map_with_all_datasets()


def create_parks_only_map():
    """
    Create a map showing only parks and green spaces.

    Returns:
        Folium map object
    """
    return create_map_with_public_areas(area_types=["park"])


def create_hiking_map():
    """
    Create a map focused on hiking trails and outdoor recreation.

    Returns:
        Folium map object
    """
    return create_map_with_public_areas(area_types=["hiking", "park", "tourism"])


def create_recreation_map():
    """
    Create a map showing recreational facilities and activities.

    Returns:
        Folium map object
    """
    return create_map_with_public_areas(area_types=["recreation", "park", "water"])


def list_available_area_types():
    """
    Display information about available public area types.
    """
    area_info = {
        "park": "Parks, gardens, nature reserves, forests, and green spaces",
        "hiking": "Hiking trails, footpaths, walking paths, and track routes",
        "recreation": "Sports facilities, playgrounds, golf courses, swimming pools",
        "beach": "Beaches and beach resorts",
        "water": "Water bodies, rivers, lakes, marinas",
        "tourism": "Tourist attractions, viewpoints, picnic sites, campsites",
        "education": "Universities, schools, libraries, and educational facilities",
    }

    print("🗺️  Available Public Area Types:")
    print("=" * 50)
    for area_type, description in area_info.items():
        print(f"📍 {area_type.upper():<12}: {description}")

    print("\n💡 Usage Examples:")
    print("   create_map_with_public_areas(['park', 'hiking'])")
    print("   create_parks_only_map()")
    print("   create_hiking_map()")
    print("   create_recreation_map()")


if __name__ == "__main__":
    print("Public Areas Utility Functions")
    print("=" * 40)

    # Show available options
    list_available_area_types()

    print("\n🏃 Creating sample maps...")

    # Create a hiking-focused map as an example
    print("\n1. Creating hiking and outdoor map...")
    hiking_map = create_hiking_map()
    hiking_map.save("hiking_areas_map.html")
    print(f"   ✓ Saved as 'hiking_areas_map.html'")

    # Create a parks-only map
    print("\n2. Creating parks and green spaces map...")
    parks_map = create_parks_only_map()
    parks_map.save("parks_only_map.html")
    print(f"   ✓ Saved as 'parks_only_map.html'")

    print(f"\n🌐 Maps saved in: {os.getcwd()}")
    print("\n📂 Files created:")
    print("   • hiking_areas_map.html - Hiking trails and outdoor areas")
    print("   • parks_only_map.html - Parks and green spaces only")
