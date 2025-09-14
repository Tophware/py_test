#!/usr/bin/env python3
"""
Refined canister trajectory analysis considering Day 16 anomaly occurred during
an active search pattern, not normal transit flight. The aircraft may have been
following a different heading during the search operation.
"""

import math
import folium
from folium import plugins
import json

# Key insight: Day 16 anomaly at 6:49AM during active search
# Aircraft was likely in search pattern, not transit flight
# Need to consider search pattern bearing vs transit bearing

# From briefing images - the aircraft bearing of 37° on Day 16
# This was likely the search pattern heading, not transit
search_pattern_coordinates = {
    "lat": 41.473666,
    "lon": -74.660742,
    "time": "6:49AM",
    "bearing": 37,  # This is the search pattern bearing
    "altitude": 65000,
    "airspeed": 750,
    "tailwind": 76,
    "crosswind": 48,  # from left
}

# Wedge search area corners (target area)
wedge_corners = [
    [40.49258082, -74.57854107],  # Corner 1: Day 18 Left (4-mile)
    [40.50053426, -74.56162256],  # Corner 2: Day 18 Right (4-mile)
    [40.52752728, -74.57756772],  # Corner 3: Day 15 cuts Day 18 (N)
    [40.51608736, -74.60373849],  # Corner 4: Day 15 cuts Day 18 (W)
]


def calculate_refined_landing_zone():
    """
    Refined calculation considering multiple scenarios:
    1. Canister released during search pattern
    2. Possible course corrections after anomaly
    3. Wind effects during 6+ minute fall time
    """

    # Base position at anomaly
    base_lat = search_pattern_coordinates["lat"]
    base_lon = search_pattern_coordinates["lon"]

    # Fall characteristics
    altitude_ft = search_pattern_coordinates["altitude"]
    altitude_m = altitude_ft * 0.3048

    # Terminal velocity for 1.5kg canister (9.5" tall x 2.625" diameter)
    # Drag coefficient for cylinder ≈ 1.2, air density at sea level ≈ 1.225 kg/m³
    # But falling from 65,000 ft means varying air density
    estimated_terminal_velocity = 45  # m/s (conservative estimate)
    fall_time = altitude_m / estimated_terminal_velocity

    print(f"Refined Analysis Parameters:")
    print(f"  Fall time: {fall_time:.1f} seconds ({fall_time/60:.1f} minutes)")
    print(f"  Search pattern bearing: {search_pattern_coordinates['bearing']}°")

    # Wind effects (convert mph to m/s)
    tailwind_ms = search_pattern_coordinates["tailwind"] * 0.44704
    crosswind_ms = search_pattern_coordinates["crosswind"] * 0.44704

    # Scenario 1: Released during search pattern heading 37°
    scenario_1 = calculate_drift_scenario(
        base_lat,
        base_lon,
        fall_time,
        search_pattern_coordinates["bearing"],
        tailwind_ms,
        crosswind_ms,
        "Search Pattern Release",
    )

    # Scenario 2: Aircraft turned toward search area after anomaly
    # Bearing toward center of wedge search area
    wedge_center_lat = sum(corner[0] for corner in wedge_corners) / len(wedge_corners)
    wedge_center_lon = sum(corner[1] for corner in wedge_corners) / len(wedge_corners)

    bearing_to_wedge = calculate_bearing(
        base_lat, base_lon, wedge_center_lat, wedge_center_lon
    )

    scenario_2 = calculate_drift_scenario(
        base_lat,
        base_lon,
        fall_time,
        bearing_to_wedge,
        tailwind_ms,
        crosswind_ms,
        "Turn Toward Search Area",
    )

    # Scenario 3: Crosswind dominant (canister pushed off course)
    crosswind_bearing = (search_pattern_coordinates["bearing"] + 90) % 360
    scenario_3 = calculate_drift_scenario(
        base_lat,
        base_lon,
        fall_time,
        crosswind_bearing,  # Primarily crosswind drift
        crosswind_ms,
        tailwind_ms,  # Swap wind components
        "Crosswind Dominant",
    )

    return [scenario_1, scenario_2, scenario_3]


def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad

    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(
        lat2_rad
    ) * math.cos(dlon)

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360


def calculate_drift_scenario(
    start_lat, start_lon, fall_time, aircraft_bearing, wind1_ms, wind2_ms, scenario_name
):
    """Calculate drift for a specific scenario"""

    # Convert wind drift to distance
    wind1_drift_m = wind1_ms * fall_time
    wind2_drift_m = wind2_ms * fall_time

    # Calculate lat/lon per meter
    lat_per_meter = 1.0 / 111000.0
    lon_per_meter = 1.0 / (111000.0 * math.cos(math.radians(start_lat)))

    # Primary wind component (along aircraft bearing)
    primary_lat_drift = (
        wind1_drift_m * math.cos(math.radians(aircraft_bearing)) * lat_per_meter
    )
    primary_lon_drift = (
        wind1_drift_m * math.sin(math.radians(aircraft_bearing)) * lon_per_meter
    )

    # Secondary wind component (perpendicular)
    secondary_bearing = (aircraft_bearing + 90) % 360
    secondary_lat_drift = (
        wind2_drift_m * math.cos(math.radians(secondary_bearing)) * lat_per_meter
    )
    secondary_lon_drift = (
        wind2_drift_m * math.sin(math.radians(secondary_bearing)) * lon_per_meter
    )

    # Total landing coordinates
    landing_lat = start_lat + primary_lat_drift + secondary_lat_drift
    landing_lon = start_lon + primary_lon_drift + secondary_lon_drift

    # Check if in wedge area
    in_wedge = point_in_polygon([landing_lat, landing_lon], wedge_corners)

    print(f"\n{scenario_name}:")
    print(f"  Aircraft bearing: {aircraft_bearing:.1f}°")
    print(f"  Landing: {landing_lat:.6f}, {landing_lon:.6f}")
    print(f"  In wedge search area: {'YES' if in_wedge else 'NO'}")

    return {
        "scenario": scenario_name,
        "aircraft_bearing": aircraft_bearing,
        "landing_lat": landing_lat,
        "landing_lon": landing_lon,
        "in_wedge": in_wedge,
        "drift_distance_m": math.sqrt((wind1_drift_m**2) + (wind2_drift_m**2)),
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


def create_multi_scenario_map(scenarios):
    """Create map showing all scenarios and likely search areas"""

    # Center on search area
    center_lat = sum(corner[0] for corner in wedge_corners) / len(wedge_corners)
    center_lon = sum(corner[1] for corner in wedge_corners) / len(wedge_corners)

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap"
    )

    # Add wedge search area
    folium.Polygon(
        locations=wedge_corners,
        color="blue",
        weight=3,
        fillColor="lightblue",
        fillOpacity=0.2,
        popup="Original Wedge Search Area",
    ).add_to(m)

    # Add anomaly location
    folium.Marker(
        [search_pattern_coordinates["lat"], search_pattern_coordinates["lon"]],
        popup=f"Day 16 Anomaly<br>6:49AM<br>Canister Release Point",
        icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
    ).add_to(m)

    # Add scenario landing zones
    colors = ["green", "orange", "purple"]
    for i, scenario in enumerate(scenarios):
        color = colors[i]

        # Landing point
        folium.Marker(
            [scenario["landing_lat"], scenario["landing_lon"]],
            popup=f"{scenario['scenario']}<br>Lat: {scenario['landing_lat']:.6f}<br>Lon: {scenario['landing_lon']:.6f}",
            icon=folium.Icon(color=color, icon="bullseye", prefix="fa"),
        ).add_to(m)

        # Search radius
        radius = 750 if scenario["in_wedge"] else 1000  # Larger radius if outside wedge
        folium.Circle(
            location=[scenario["landing_lat"], scenario["landing_lon"]],
            radius=radius,
            color=color,
            fillColor=color,
            fillOpacity=0.2,
            popup=f'{scenario["scenario"]}<br>{radius}m search radius',
        ).add_to(m)

    # Add satellite layer option
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def identify_public_access_areas():
    """Identify likely public access areas near landing zones"""
    print(f"\n=== PUBLIC ACCESS ANALYSIS ===")
    print(f"Based on the refined scenarios, look for:")
    print(f"1. State parks and forests")
    print(f"2. Hiking trails and nature preserves")
    print(f"3. Public boat launches and fishing areas")
    print(f"4. Municipal parks with wooded areas")
    print(f"5. Wildlife management areas")
    print(f"\nTarget characteristics:")
    print(f"- Wooded areas that provide cover")
    print(f"- Easily accessible by foot")
    print(f'- Areas where a 9.5" canister might remain unnoticed')
    print(f"- Near but not directly on main trails")


if __name__ == "__main__":
    print("=== REFINED CANISTER LANDING ANALYSIS ===")
    print("Considering Day 16 anomaly during active search operations\n")

    # Calculate scenarios
    scenarios = calculate_refined_landing_zone()

    # Check which scenarios land in search area
    in_wedge_scenarios = [s for s in scenarios if s["in_wedge"]]

    if in_wedge_scenarios:
        print(
            f"\n✓ {len(in_wedge_scenarios)} scenario(s) land within wedge search area!"
        )
        print("Focus search efforts on these locations.")
    else:
        print("\n⚠ No scenarios land directly in wedge area.")
        print("Consider expanding search or checking nearby public areas.")

    # Create comprehensive map
    scenario_map = create_multi_scenario_map(scenarios)
    scenario_map.save("refined_canister_scenarios.html")
    print(f"\nScenario map saved as: refined_canister_scenarios.html")

    # Public access analysis
    identify_public_access_areas()

    # Save scenario data
    with open("refined_scenarios.json", "w") as f:
        json.dump(scenarios, f, indent=2)
    print(f"Scenario data saved as: refined_scenarios.json")
