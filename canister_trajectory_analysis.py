#!/usr/bin/env python3
"""
Analyze canister trajectory and probable landing zone based on briefing data.
Focus on Day 16 anomaly with wind conditions and canister separation.
"""

import math
import folium
from folium import plugins
import json

# Flight path coordinates from briefing images
flight_coordinates = [
    {"day": 1, "lat": 41.215671, "lon": -74.906966, "date": "20250827"},
    {"day": 4, "lat": 41.256498, "lon": -74.750476, "date": "20250830"},
    {"day": 7, "lat": 41.320632, "lon": -74.707031, "date": "20250902"},
    {"day": 10, "lat": 41.455211, "lon": -74.507323, "date": "20250905"},
    {"day": 13, "lat": 41.514417, "lon": -74.596033, "date": "20250908"},
    {"day": 16, "lat": 41.473666, "lon": -74.660742, "date": "20250911"},  # Anomaly day
]

# Wedge search area corners
wedge_corners = [
    [40.49258082, -74.57854107],  # Corner 1: Day 18 Left (4-mile)
    [40.50053426, -74.56162256],  # Corner 2: Day 18 Right (4-mile)
    [40.52752728, -74.57756772],  # Corner 3: Day 15 cuts Day 18 (N)
    [40.51608736, -74.60373849],  # Corner 4: Day 15 cuts Day 18 (W)
]

# Day 16 conditions from briefing
day_16_conditions = {
    "time_of_anomaly": "6:49AM",
    "altitude": 65000,  # feet
    "airspeed": 750,  # mph
    "mass": 1.5,  # kg
    "bearing": 37,  # degrees
    "dimensions": {"height": 9.5, "diameter": 2.625},  # inches
    "tailwind": 76,  # mph
    "crosswind": 48,  # mph from left
    "temperature_variations": True,
    "coordinates": {"lat": 41.473666, "lon": -74.660742},
}


def calculate_trajectory_bearing(coords_list):
    """Calculate the general trajectory bearing from the flight path"""
    if len(coords_list) < 2:
        return None

    # Use last few points to get current trajectory
    start = coords_list[-3] if len(coords_list) >= 3 else coords_list[-2]
    end = coords_list[-1]

    lat1, lon1 = math.radians(start["lat"]), math.radians(start["lon"])
    lat2, lon2 = math.radians(end["lat"]), math.radians(end["lon"])

    dlon = lon2 - lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        dlon
    )

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    return bearing


def calculate_canister_drift(start_lat, start_lon, altitude_ft, wind_conditions):
    """
    Calculate where canister would drift based on wind conditions and fall time.
    """
    # Convert altitude to meters for calculation
    altitude_m = altitude_ft * 0.3048

    # Estimate fall time (simplified terminal velocity calculation)
    # For a 1.5kg canister, assume terminal velocity ~50 m/s
    terminal_velocity = 50  # m/s
    fall_time = altitude_m / terminal_velocity  # seconds

    # Wind components
    tailwind_ms = wind_conditions["tailwind"] * 0.44704  # mph to m/s
    crosswind_ms = wind_conditions["crosswind"] * 0.44704  # mph to m/s

    # Flight bearing from aircraft
    aircraft_bearing = wind_conditions["bearing"]  # 37 degrees

    # Calculate drift during fall
    # Tailwind pushes in direction of flight
    tailwind_drift_m = tailwind_ms * fall_time

    # Crosswind pushes perpendicular to flight (from left = 90 degrees counterclockwise)
    crosswind_bearing = (aircraft_bearing + 90) % 360
    crosswind_drift_m = crosswind_ms * fall_time

    # Convert drift distances to lat/lon changes
    # Rough conversion: 1 degree lat ≈ 111,000m, 1 degree lon ≈ 111,000m * cos(lat)
    lat_per_meter = 1.0 / 111000.0
    lon_per_meter = 1.0 / (111000.0 * math.cos(math.radians(start_lat)))

    # Calculate tailwind drift components
    tailwind_lat_drift = (
        tailwind_drift_m * math.cos(math.radians(aircraft_bearing)) * lat_per_meter
    )
    tailwind_lon_drift = (
        tailwind_drift_m * math.sin(math.radians(aircraft_bearing)) * lon_per_meter
    )

    # Calculate crosswind drift components
    crosswind_lat_drift = (
        crosswind_drift_m * math.cos(math.radians(crosswind_bearing)) * lat_per_meter
    )
    crosswind_lon_drift = (
        crosswind_drift_m * math.sin(math.radians(crosswind_bearing)) * lon_per_meter
    )

    # Total drift
    total_lat_drift = tailwind_lat_drift + crosswind_lat_drift
    total_lon_drift = tailwind_lon_drift + crosswind_lon_drift

    # Landing coordinates
    landing_lat = start_lat + total_lat_drift
    landing_lon = start_lon + total_lon_drift

    return {
        "landing_lat": landing_lat,
        "landing_lon": landing_lon,
        "fall_time_seconds": fall_time,
        "drift_distance_m": math.sqrt((tailwind_drift_m + crosswind_drift_m) ** 2),
        "drift_components": {
            "tailwind_m": tailwind_drift_m,
            "crosswind_m": crosswind_drift_m,
            "total_lat_drift": total_lat_drift,
            "total_lon_drift": total_lon_drift,
        },
    }


def point_in_polygon(point, polygon):
    """Check if point is inside polygon using ray casting algorithm"""
    x, y = point[0], point[1]
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def analyze_trajectory():
    """Main analysis function"""
    print("=== CANISTER TRAJECTORY ANALYSIS ===")
    print()

    # Calculate flight trajectory bearing
    trajectory_bearing = calculate_trajectory_bearing(flight_coordinates)
    print(f"Flight trajectory bearing: {trajectory_bearing:.1f}°")

    # Day 16 anomaly analysis
    day_16 = day_16_conditions
    print(f"\nDay 16 Anomaly Conditions:")
    print(
        f"  Location: {day_16['coordinates']['lat']:.6f}, {day_16['coordinates']['lon']:.6f}"
    )
    print(f"  Time: {day_16['time_of_anomaly']}")
    print(f"  Altitude: {day_16['altitude']:,} ft")
    print(f"  Aircraft bearing: {day_16['bearing']}°")
    print(f"  Tailwind: {day_16['tailwind']} mph")
    print(f"  Crosswind: {day_16['crosswind']} mph from left")

    # Calculate canister landing zone
    drift_analysis = calculate_canister_drift(
        day_16["coordinates"]["lat"],
        day_16["coordinates"]["lon"],
        day_16["altitude"],
        day_16,
    )

    print(f"\nCanister Drift Analysis:")
    print(f"  Estimated fall time: {drift_analysis['fall_time_seconds']:.1f} seconds")
    print(f"  Total drift distance: {drift_analysis['drift_distance_m']:.0f} meters")
    print(
        f"  Probable landing: {drift_analysis['landing_lat']:.6f}, {drift_analysis['landing_lon']:.6f}"
    )

    # Check if landing is within wedge search area
    landing_point = [drift_analysis["landing_lat"], drift_analysis["landing_lon"]]
    in_wedge = point_in_polygon(landing_point, wedge_corners)

    print(f"\nSearch Area Analysis:")
    print(f"  Landing within wedge search area: {'YES' if in_wedge else 'NO'}")

    if in_wedge:
        print("  ✓ Canister is likely within the defined search wedge!")
        print(
            "  ✓ Focus search on wooded, publicly accessible areas near landing coordinates"
        )
    else:
        print("  ⚠ Canister may be outside current search wedge")
        print("  Consider expanding search area or refining trajectory calculations")

    return {
        "trajectory_bearing": trajectory_bearing,
        "day_16_conditions": day_16,
        "drift_analysis": drift_analysis,
        "in_search_area": in_wedge,
        "landing_coordinates": landing_point,
    }


def create_trajectory_map(analysis_result):
    """Create interactive map showing trajectory and probable landing zone"""

    # Center map on landing area
    center_lat = analysis_result["landing_coordinates"][0]
    center_lon = analysis_result["landing_coordinates"][1]

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap"
    )

    # Add wedge search area
    folium.Polygon(
        locations=wedge_corners,
        color="blue",
        weight=3,
        fillColor="lightblue",
        fillOpacity=0.2,
        popup="Wedge Search Area",
    ).add_to(m)

    # Add flight path
    flight_path = [[coord["lat"], coord["lon"]] for coord in flight_coordinates]
    folium.PolyLine(
        flight_path, color="red", weight=3, opacity=0.8, popup="Flight Path"
    ).add_to(m)

    # Add flight coordinates as markers
    for i, coord in enumerate(flight_coordinates):
        folium.Marker(
            [coord["lat"], coord["lon"]],
            popup=f"Day {coord['day']}: {coord['date']}",
            icon=folium.Icon(color="red", icon="plane"),
        ).add_to(m)

    # Add Day 16 anomaly location (canister release point)
    day_16 = analysis_result["day_16_conditions"]
    folium.Marker(
        [day_16["coordinates"]["lat"], day_16["coordinates"]["lon"]],
        popup=f"Day 16 Anomaly<br>Canister Release Point<br>{day_16['time_of_anomaly']}",
        icon=folium.Icon(color="orange", icon="exclamation-triangle", prefix="fa"),
    ).add_to(m)

    # Add probable landing zone
    landing_lat, landing_lon = analysis_result["landing_coordinates"]
    folium.Marker(
        [landing_lat, landing_lon],
        popup=f"Probable Canister Landing<br>Lat: {landing_lat:.6f}<br>Lon: {landing_lon:.6f}",
        icon=folium.Icon(color="green", icon="bullseye", prefix="fa"),
    ).add_to(m)

    # Add uncertainty circle around landing zone
    folium.Circle(
        location=[landing_lat, landing_lon],
        radius=500,  # 500 meter uncertainty radius
        color="green",
        fillColor="lightgreen",
        fillOpacity=0.3,
        popup="500m Search Radius",
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m


if __name__ == "__main__":
    # Run analysis
    analysis = analyze_trajectory()

    # Create map
    trajectory_map = create_trajectory_map(analysis)

    # Save map
    map_filename = "canister_landing_analysis.html"
    trajectory_map.save(map_filename)
    print(f"\nInteractive map saved as: {map_filename}")

    # Save analysis data
    analysis_filename = "canister_trajectory_analysis.json"
    with open(analysis_filename, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis data saved as: {analysis_filename}")
