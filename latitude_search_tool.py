#!/usr/bin/env python3
"""
LATITUDE SEARCH TOOL
Tool to help narrow canister search when you get a latitude coordinate.
Creates focused search bands and updates the map.
"""

import folium
import math
from shapely.geometry import Point, Polygon, LineString
import json


def calculate_latitude_search_band(drop_point, radius_miles, given_latitude):
    """Calculate the search band when latitude intersects with search circle."""

    center_lat, center_lon = drop_point

    # Convert radius to degrees (approximate)
    radius_degrees = radius_miles / 69.0  # roughly 69 miles per degree latitude

    # Distance from circle center to the given latitude line
    lat_distance = abs(given_latitude - center_lat)

    if lat_distance > radius_degrees:
        return None, "Latitude line doesn't intersect the search circle"

    # Using Pythagorean theorem to find where latitude line intersects circle
    half_chord_degrees = math.sqrt(radius_degrees**2 - lat_distance**2)
    half_chord_miles = half_chord_degrees * 69.0

    # Calculate intersection points
    west_intersection = (
        center_lon - half_chord_degrees * 1.3
    )  # adjust for longitude scaling
    east_intersection = center_lon + half_chord_degrees * 1.3

    # Search band coordinates
    search_band = {
        "latitude": given_latitude,
        "west_point": [given_latitude, west_intersection],
        "east_point": [given_latitude, east_intersection],
        "band_width_miles": 2 * half_chord_miles,
        "center_distance_miles": lat_distance * 69.0,
    }

    # Calculate area reduction
    circle_area = math.pi * radius_miles**2
    band_area = search_band["band_width_miles"] * 0.05  # assume 0.05 mile search width
    area_reduction_percent = (1 - band_area / circle_area) * 100

    search_band["area_reduction_percent"] = area_reduction_percent

    return search_band, "Success"


def create_latitude_focused_map(
    drop_point, search_radius_miles, given_latitude, corners
):
    """Create a map focused on the latitude search band."""

    # Calculate search band
    search_band, status = calculate_latitude_search_band(
        drop_point, search_radius_miles, given_latitude
    )

    if not search_band:
        print(f"Error: {status}")
        return None

    # Create map centered on the search band
    center_lat = given_latitude
    center_lon = drop_point[1]

    lat_map = folium.Map(location=[center_lat, center_lon], zoom_start=16)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(lat_map)

    # Add the original search circle
    folium.Circle(
        location=drop_point,
        radius=search_radius_miles * 1609.34,  # convert miles to meters
        popup="Original 0.5-mile search zone",
        tooltip="Original Search Circle",
        color="blue",
        weight=2,
        fill=True,
        fillColor="lightblue",
        fillOpacity=0.1,
    ).add_to(lat_map)

    # Add the latitude line across the map
    folium.PolyLine(
        locations=[
            [given_latitude, center_lon - 0.01],  # extend line beyond circle
            [given_latitude, center_lon + 0.01],
        ],
        popup=f"<b>LATITUDE LINE: {given_latitude}</b><br>Focus your search along this line!",
        tooltip=f"Latitude: {given_latitude}",
        color="red",
        weight=4,
        opacity=0.8,
    ).add_to(lat_map)

    # Add intersection points
    folium.Marker(
        location=search_band["west_point"],
        popup=f"<b>West Intersection</b><br>Lat: {search_band['west_point'][0]:.6f}<br>Lon: {search_band['west_point'][1]:.6f}",
        tooltip="West Search Boundary",
        icon=folium.Icon(color="red", icon="arrow-left", prefix="fa"),
    ).add_to(lat_map)

    folium.Marker(
        location=search_band["east_point"],
        popup=f"<b>East Intersection</b><br>Lat: {search_band['east_point'][0]:.6f}<br>Lon: {search_band['east_point'][1]:.6f}",
        tooltip="East Search Boundary",
        icon=folium.Icon(color="red", icon="arrow-right", prefix="fa"),
    ).add_to(lat_map)

    # Add drop point
    folium.Marker(
        location=drop_point,
        popup=f"<b>CANISTER DROP POINT</b><br>Original drop location",
        tooltip="Drop Point",
        icon=folium.Icon(color="orange", icon="bullseye", prefix="fa"),
    ).add_to(lat_map)

    # Add focused search zone (rectangle along latitude)
    search_height = 0.001  # very narrow band for precise search
    folium.Rectangle(
        bounds=[
            [given_latitude - search_height, search_band["west_point"][1]],
            [given_latitude + search_height, search_band["east_point"][1]],
        ],
        popup=f"<b>FOCUSED SEARCH BAND</b><br>Width: {search_band['band_width_miles']:.3f} miles<br>Area reduction: {search_band['area_reduction_percent']:.1f}%<br><b>Search only in this band!</b>",
        tooltip="Focused Search Band",
        color="yellow",
        weight=3,
        fill=True,
        fillColor="yellow",
        fillOpacity=0.3,
    ).add_to(lat_map)

    # Add layer control
    folium.LayerControl().add_to(lat_map)

    return lat_map, search_band


def print_search_strategy(search_band, given_latitude):
    """Print the optimal search strategy with the latitude."""

    print("\n" + "=" * 60)
    print("LATITUDE-FOCUSED SEARCH STRATEGY")
    print("=" * 60)

    print(f"Latitude provided: {given_latitude}")
    print(f"Search band width: {search_band['band_width_miles']:.3f} miles")
    print(f"Area reduction: {search_band['area_reduction_percent']:.1f}%")
    print(
        f"Distance from drop center: {search_band['center_distance_miles']:.3f} miles"
    )

    print(f"\nSEARCH COORDINATES:")
    print(
        f"  West boundary: {search_band['west_point'][0]:.6f}, {search_band['west_point'][1]:.6f}"
    )
    print(
        f"  East boundary: {search_band['east_point'][0]:.6f}, {search_band['east_point'][1]:.6f}"
    )

    print(f"\nOPTIMAL SEARCH METHOD:")
    print(f"  1. Use GPS to navigate to latitude {given_latitude}")
    print(f"  2. Walk east-west along this exact latitude line")
    print(f"  3. Focus on these area types:")
    print(f"     - Wooded areas with public access")
    print(f"     - Trail intersections at this latitude")
    print(f"     - Forest edges and clearings")
    print(f"     - Cemetery sections (if any)")
    print(f"  4. Search within 50 feet north/south of the latitude line")
    print(f'  5. Look for the canister: 9.5" tall x 2.6" diameter')

    print(f"\nGPS SEARCH PATTERN:")
    print(
        f"  - Set GPS waypoint at: {given_latitude:.6f}, {search_band['west_point'][1]:.6f}"
    )
    print(f"  - Walk east maintaining exact latitude: {given_latitude}")
    print(f"  - End at: {given_latitude:.6f}, {search_band['east_point'][1]:.6f}")
    print(f"  - Total distance: ~{search_band['band_width_miles']:.2f} miles")


def main():
    """Main function to demonstrate latitude search tool."""

    print("LATITUDE SEARCH TOOL")
    print("=" * 40)

    # Canister drop point (from previous analysis)
    drop_point = [40.514417, -74.596033]
    search_radius_miles = 0.5

    # Wedge corners (from your search area)
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    # Example latitude (you would replace this with your actual latitude)
    example_latitude = 40.515000

    print(f"Drop Point: {drop_point}")
    print(f"Search Radius: {search_radius_miles} miles")
    print(f"Example Latitude: {example_latitude}")

    # Create the focused map
    lat_map, search_band = create_latitude_focused_map(
        drop_point, search_radius_miles, example_latitude, corners
    )

    if lat_map:
        # Save the map
        output_file = f"latitude_search_{example_latitude}.html"
        lat_map.save(output_file)
        print(f"\nMap saved as: {output_file}")

        # Print search strategy
        print_search_strategy(search_band, example_latitude)

        return lat_map
    else:
        print("Could not create latitude search map")
        return None


if __name__ == "__main__":
    main()
