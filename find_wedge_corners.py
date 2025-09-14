#!/usr/bin/env python3
"""
Find the 4 corner coordinates where Day 15 cuts into Day 18 wedge area
"""

import math
from shapely.geometry import LineString, Point


def main():
    print("Finding Day 15/Day 18 Wedge Intersection Points")
    print("=" * 50)

    # Day 15 center point (New Hope Bridge)
    day15_center = [40.364551, -74.950404]

    # Day 18 center point (High Voltage Lines)
    day18_center = [40.44766, -74.530389]

    # Day 18 boundary lines from the HTML
    day18_left_line = [[40.44766, -74.530389], [40.49258081626851, -74.57854106978262]]
    day18_right_line = [
        [40.44766, -74.530389],
        [40.500534257083714, -74.56162256270201],
    ]
    day18_center_line = [
        [40.44766, -74.530389],
        [40.533969075286976, -74.60045081698073],
    ]

    # Day 15 boundary lines from the HTML
    day15_left_line = [[40.364551, -74.950404], [40.43667047680688, -74.78541828511084]]
    day15_right_line = [
        [40.364551, -74.950404],
        [40.36415376095365, -74.76019590932249],
    ]
    day15_center_line = [
        [40.364551, -74.950404],
        [40.45736640544898, -74.49074939208452],
    ]

    print("Day 18 boundaries:")
    print(f"  Center: {day18_center}")
    print(f"  Left line: {day18_left_line[0]} -> {day18_left_line[1]}")
    print(f"  Right line: {day18_right_line[0]} -> {day18_right_line[1]}")
    print(f"  Center line: {day18_center_line[0]} -> {day18_center_line[1]}")

    print("\nDay 15 boundaries:")
    print(f"  Center: {day15_center}")
    print(f"  Left line: {day15_left_line[0]} -> {day15_left_line[1]}")
    print(f"  Right line: {day15_right_line[0]} -> {day15_right_line[1]}")
    print(f"  Center line: {day15_center_line[0]} -> {day15_center_line[1]}")

    # Calculate distance in degrees (rough approximation)
    def distance_between_points(p1, p2):
        lat_diff = p2[0] - p1[0]
        lon_diff = p2[1] - p1[1]
        return math.sqrt(lat_diff**2 + lon_diff**2)

    # Find points at 4 miles along Day 18 boundaries
    # 4 miles ≈ 0.058 degrees at this latitude
    miles_to_degrees = 0.0145  # Rough conversion for this area
    four_miles_deg = 4 * miles_to_degrees

    def point_along_line(start, end, distance_ratio):
        """Find a point along a line at a specific distance ratio (0-1)"""
        lat = start[0] + (end[0] - start[0]) * distance_ratio
        lon = start[1] + (end[1] - start[1]) * distance_ratio
        return [lat, lon]

    # Calculate total distance of Day 18 lines
    day18_left_total_dist = distance_between_points(
        day18_left_line[0], day18_left_line[1]
    )
    day18_right_total_dist = distance_between_points(
        day18_right_line[0], day18_right_line[1]
    )

    # Find 4-mile points along Day 18 boundaries
    four_mile_ratio_left = four_miles_deg / day18_left_total_dist
    four_mile_ratio_right = four_miles_deg / day18_right_total_dist

    day18_left_4mile = point_along_line(
        day18_left_line[0], day18_left_line[1], four_mile_ratio_left
    )
    day18_right_4mile = point_along_line(
        day18_right_line[0], day18_right_line[1], four_mile_ratio_right
    )

    print(f"\nDay 18 inner boundary (4-mile mark):")
    print(
        f"  Left side at 4 miles:  [{day18_left_4mile[0]:.8f}, {day18_left_4mile[1]:.8f}]"
    )
    print(
        f"  Right side at 4 miles: [{day18_right_4mile[0]:.8f}, {day18_right_4mile[1]:.8f}]"
    )

    # Create LineString objects for intersection calculations
    day15_left_linestring = LineString(day15_left_line)
    day15_right_linestring = LineString(day15_right_line)
    day18_left_linestring = LineString(day18_left_line)
    day18_right_linestring = LineString(day18_right_line)

    # Find intersections between Day 15 boundaries and Day 18 boundaries
    intersections = []

    # Check Day 15 left line intersecting Day 18 left line
    intersection1 = day15_left_linestring.intersection(day18_left_linestring)
    if not intersection1.is_empty and hasattr(intersection1, "x"):
        intersections.append([intersection1.y, intersection1.x])
        print(
            f"Day 15 left ∩ Day 18 left: [{intersection1.y:.8f}, {intersection1.x:.8f}]"
        )

    # Check Day 15 left line intersecting Day 18 right line
    intersection2 = day15_left_linestring.intersection(day18_right_linestring)
    if not intersection2.is_empty and hasattr(intersection2, "x"):
        intersections.append([intersection2.y, intersection2.x])
        print(
            f"Day 15 left ∩ Day 18 right: [{intersection2.y:.8f}, {intersection2.x:.8f}]"
        )

    # Check Day 15 right line intersecting Day 18 left line
    intersection3 = day15_right_linestring.intersection(day18_left_linestring)
    if not intersection3.is_empty and hasattr(intersection3, "x"):
        intersections.append([intersection3.y, intersection3.x])
        print(
            f"Day 15 right ∩ Day 18 left: [{intersection3.y:.8f}, {intersection3.x:.8f}]"
        )

    # Check Day 15 right line intersecting Day 18 right line
    intersection4 = day15_right_linestring.intersection(day18_right_linestring)
    if not intersection4.is_empty and hasattr(intersection4, "x"):
        intersections.append([intersection4.y, intersection4.x])
        print(
            f"Day 15 right ∩ Day 18 right: [{intersection4.y:.8f}, {intersection4.x:.8f}]"
        )

    print(f"\nFound {len(intersections)} boundary intersections")

    # The 4 corners should be:
    # 1. Day 18 left at 4 miles
    # 2. Day 18 right at 4 miles
    # 3. Where Day 15 cuts Day 18 (intersection points)
    print(f"\n=== THE 4 CORNER COORDINATES ===")
    print(
        f"1. Day 18 Left at 4-mile mark:  [{day18_left_4mile[0]:.8f}, {day18_left_4mile[1]:.8f}]"
    )
    print(
        f"2. Day 18 Right at 4-mile mark: [{day18_right_4mile[0]:.8f}, {day18_right_4mile[1]:.8f}]"
    )

    if len(intersections) >= 2:
        print(
            f"3. Day 15/Day 18 intersection:   [{intersections[0][0]:.8f}, {intersections[0][1]:.8f}]"
        )
        print(
            f"4. Day 15/Day 18 intersection:   [{intersections[1][0]:.8f}, {intersections[1][1]:.8f}]"
        )
    else:
        print("Could not find Day 15/Day 18 boundary intersections")

        # Alternative approach: look at the polygon coordinates more carefully
        print("\nLet me check the polygon endpoints...")

        # Day 15 polygon goes from one edge to the other, then back along arc
        # Day 18 polygon does the same
        # Look at where they might intersect based on coordinates

        day15_coords = [
            [40.43667047680688, -74.78541828511084],
            [40.43335508327552, -74.78299710693108],
            [40.42999253486232, -74.78069066107366],
            [40.42658513609001, -74.77850052826138],
            [40.4231352222195, -74.77642820950186],
        ]

        day18_coords = [
            [40.49258081626851, -74.57854106978262],
            [40.493056618655906, -74.57776428199409],
            [40.4935246425664, -74.5769793766949],
            [40.4939848078065, -74.57618648837449],
            [40.494437035529266, -74.57538575289023],
        ]

        print("Day 15 polygon starts:", day15_coords[:3])
        print("Day 18 polygon starts:", day18_coords[:3])


if __name__ == "__main__":
    main()
