"""
Public Areas Demo - Enhanced Map with Public Space Identification

This demo shows how to identify and display public areas like parks, hiking trails,
recreation facilities, and other publicly accessible spaces on your search area maps.
"""

import folium
from public_areas import PublicAreasOverlay


def create_enhanced_demo_map():
    """
    Create a demonstration map focused on public areas around the search sectors.
    """
    print("Creating enhanced public areas demonstration...")

    # Initialize the public areas overlay
    overlay = PublicAreasOverlay()

    # Define the search area around your current sectors
    # This covers the area between your two main search zones
    demo_bounds = (40.3, -75.0, 40.5, -74.4)  # (south, west, north, east)

    # Calculate center point for the map
    center_lat = (demo_bounds[0] + demo_bounds[2]) / 2
    center_lon = (demo_bounds[1] + demo_bounds[3]) / 2

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    # Add multiple tile layer options
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add topographical view for hiking areas
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add your search sectors for reference
    add_demo_sectors(m)

    # Add comprehensive public areas overlay
    all_area_types = [
        "park",
        "hiking",
        "recreation",
        "beach",
        "water",
        "tourism",
        "education",
    ]

    try:
        print("Fetching public areas data from OpenStreetMap...")
        m = overlay.add_public_areas_to_map(m, demo_bounds, all_area_types)
        print("✓ Public areas overlay added successfully!")

        # Add a custom marker to show the demo focus area
        folium.Marker(
            location=[center_lat, center_lon],
            popup="<b>Demo Focus Area</b><br>Public areas are displayed for this region",
            tooltip="Demo Center",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)

        # Add a bounds rectangle to show the search area
        folium.Rectangle(
            bounds=[[demo_bounds[0], demo_bounds[1]], [demo_bounds[2], demo_bounds[3]]],
            popup="Public Areas Search Boundary",
            tooltip="Search Area Bounds",
            color="red",
            weight=2,
            fill=False,
            dashArray="10, 10",
        ).add_to(m)

    except Exception as e:
        print(f"Warning: Could not fetch all public areas data: {e}")
        print("This might be due to network connectivity or API limits.")

    # Add layer control to switch between views and overlays
    folium.LayerControl().add_to(m)

    # Save the enhanced demo map
    demo_map_name = "public_areas_enhanced_demo.html"
    m.save(demo_map_name)

    print(f"\n🗺️  Enhanced demo map saved as '{demo_map_name}'")
    print("\n📍 Public Areas Identified:")
    print("   🌳 Parks and green spaces (nature reserves, gardens, forests)")
    print("   🥾 Hiking trails and footpaths")
    print("   ⚽ Recreation facilities (sports centers, playgrounds, golf courses)")
    print("   🏖️  Beach and water areas")
    print("   🏛️  Tourism attractions and viewpoints")
    print("   🎓 Educational facilities (universities, libraries)")

    print(f"\n🌐 Open the map to explore: file://{os.path.abspath(demo_map_name)}")
    print("\n💡 Tips for using the map:")
    print(
        "   • Use the layer control (top right) to switch between street/satellite/topo views"
    )
    print("   • Click on colored areas and markers to see details about public spaces")
    print("   • Different colors represent different types of public areas")
    print("   • Green = Parks, Brown = Hiking, Blue = Recreation, etc.")

    return m


def add_demo_sectors(map_obj):
    """Add simplified demonstration sectors to show context."""

    # New Hope Bridge area (simplified)
    folium.Circle(
        location=[40.364551, -74.950404],
        radius=20000,  # 20km radius
        popup="Day 15 - New Hope Bridge Search Area",
        tooltip="Search Sector",
        color="blue",
        weight=2,
        fill=True,
        fillColor="lightblue",
        fillOpacity=0.1,
    ).add_to(map_obj)

    folium.Marker(
        location=[40.364551, -74.950404],
        popup="Day 15 - New Hope Bridge",
        tooltip="Search Center",
        icon=folium.Icon(color="blue", icon="star"),
    ).add_to(map_obj)

    # High Voltage Lines area (simplified)
    folium.Circle(
        location=[40.447660, -74.530389],
        radius=7000,  # 7km radius
        popup="Day 18 - High Voltage Lines Search Area",
        tooltip="Search Sector",
        color="green",
        weight=2,
        fill=True,
        fillColor="lightgreen",
        fillOpacity=0.1,
    ).add_to(map_obj)

    folium.Marker(
        location=[40.447660, -74.530389],
        popup="Day 18 - High Voltage Lines",
        tooltip="Search Center",
        icon=folium.Icon(color="green", icon="star"),
    ).add_to(map_obj)


if __name__ == "__main__":
    import os

    create_enhanced_demo_map()
