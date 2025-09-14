#!/usr/bin/env python3
"""
Simple map plotting the 4 corner coordinates of the Day 15 and Day 18 overlap area
"""

import folium


def main():
    # The 4 corner coordinates of the overlap area
    corners = [
        [40.49258082, -74.60373849],  # Southwest
        [40.49258082, -74.56162256],  # Southeast
        [40.52752728, -74.60373849],  # Northwest
        [40.52752728, -74.56162256],  # Northeast
    ]

    # Calculate center point for the map
    center_lat = sum(coord[0] for coord in corners) / len(corners)
    center_lon = sum(coord[1] for coord in corners) / len(corners)

    # Create a map centered on the overlap area
    map_overlap = folium.Map(
        location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap"
    )

    # Add markers for each corner
    corner_names = ["Southwest", "Southeast", "Northwest", "Northeast"]
    corner_colors = ["red", "blue", "green", "purple"]

    for i, (coord, name, color) in enumerate(zip(corners, corner_names, corner_colors)):
        folium.Marker(
            location=coord,
            popup=f"{name} Corner<br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"{name} Corner",
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(map_overlap)

    # Create a rectangle to show the overlap area
    rectangle_coords = [
        [corners[0][0], corners[0][1]],  # Southwest
        [corners[1][0], corners[1][1]],  # Southeast
        [corners[3][0], corners[3][1]],  # Northeast
        [corners[2][0], corners[2][1]],  # Northwest
        [corners[0][0], corners[0][1]],  # Back to Southwest (close the polygon)
    ]

    folium.Polygon(
        locations=rectangle_coords,
        color="red",
        weight=3,
        fillColor="yellow",
        fillOpacity=0.3,
        popup="Day 15 & Day 18 Overlap Area<br>Search Zone: ~3.51 square miles",
    ).add_to(map_overlap)

    # Add a title to the map
    title_html = """
                 <h3 align="center" style="font-size:20px"><b>Day 15 & Day 18 Overlap Search Area</b></h3>
                 <p align="center">Yellow highlighted area shows where Day 15 and Day 18 search zones intersect</p>
                 """
    map_overlap.get_root().html.add_child(folium.Element(title_html))

    # Save the map
    output_file = "overlap_search_area.html"
    map_overlap.save(output_file)

    print("Overlap Area Map Created!")
    print("=" * 30)
    print(f"Map saved as: {output_file}")
    print("\nCorner Coordinates:")
    for i, (coord, name) in enumerate(zip(corners, corner_names)):
        print(f"{i+1}. {name:10}: [{coord[0]:.8f}, {coord[1]:.8f}]")

    print(f"\nCenter point: [{center_lat:.8f}, {center_lon:.8f}]")
    print("Area: ~3.51 square miles (2.27 miles × 2.41 miles)")


if __name__ == "__main__":
    main()
