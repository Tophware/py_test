#!/usr/bin/env python3
"""
Find the 4 corner coordinates where Day 15 cuts Day 18 wedge by analyzing polygon boundaries
"""

from shapely.geometry import Polygon, LineString, Point
import math


def main():
    print("Day 15/Day 18 Wedge Intersection Analysis")
    print("=" * 45)

    # Day 18 center and 4-mile radius calculation
    day18_center = [40.44766, -74.530389]

    # From the polygon, Day 18 starts at the center and goes out
    # The first point after center should be on the left boundary at ~4 miles
    day18_left_4mile = [
        40.49258081626851,
        -74.57854106978262,
    ]  # First point in Day 18 polygon
    day18_right_4mile = [40.500534257083714, -74.56162256270201]  # Last inner point

    print("Day 18 inner boundary points (4-mile mark):")
    print(f"  Left:  [{day18_left_4mile[0]:.8f}, {day18_left_4mile[1]:.8f}]")
    print(f"  Right: [{day18_right_4mile[0]:.8f}, {day18_right_4mile[1]:.8f}]")

    # Day 15 polygon coordinates (looking for where it intersects Day 18)
    day_15_coords = [
        [40.43667047680688, -74.78541828511084],
        [40.43335508327552, -74.78299710693108],
        [40.42999253486232, -74.78069066107366],
        [40.42658513609001, -74.77850052826138],
        [40.4231352222195, -74.77642820950186],
        [40.41964515764942, -74.77447512505886],
        [40.416117334295706, -74.7726426134789],
        [40.41255416995226, -74.77093193067388],
        [40.40895810663394, -74.76934424906034],
        [40.40533160890292, -74.76788065675596],
        [40.40167716217959, -74.76654215683381],
        [40.3979972710392, -74.76532966663486],
        [40.39429445749531, -74.76424401713932],
        [40.39057125927138, -74.76328595239713],
        [40.38683022806149, -74.76245612901802],
        [40.38307392778155, -74.76175511572147],
        [40.379304932812154, -74.76118339294699],
        [40.37552582623419, -74.7607413525248],
        [40.37173919805852, -74.76042929740733],
        [40.36794764345096, -74.76024744146156],
        [40.36415376095365, -74.76019590932249],
        [40.363557902384116, -74.47488377330622],
        [40.3730426086274, -74.4750126036539],
        [40.3825214951463, -74.47546724351831],
        [40.391988065585466, -74.47624738131199],
        [40.401435832030394, -74.47735248236746],
        [40.41085831945389, -74.47878178930367],
        [40.42024907015372, -74.48053432254504],
        [40.42960164817846, -74.48260888099281],
        [40.43890964373829, -74.48500404284827],
        [40.448166677598, -74.48771816658713],
        [40.45736640544898, -74.49074939208452],
        [40.466502522257294, -74.49409564188991],
        [40.47556876658485, -74.49775462265085],
        [40.48455892488065, -74.50172382668468],
        [40.49346683573926, -74.50600053369723],
        [40.50228639412355, -74.51058181264713],
        [40.51101155554874, -74.51546452375463],
        [40.519636340225034, -74.52064532065344],
        [40.52815483715581, -74.52612065268416],
        [40.5365612081888, -74.53188676732769],
        [40.5448496920172, -74.5379397127771],
        [40.43667047680688, -74.78541828511084],
    ]

    # Day 18 polygon coordinates
    day_18_coords = [
        [40.49258081626851, -74.57854106978262],
        [40.493056618655906, -74.57776428199409],
        [40.4935246425664, -74.5769793766949],
        [40.4939848078065, -74.57618648837449],
        [40.494437035529266, -74.57538575289023],
        [40.4948812482478, -74.57457730744399],
        [40.49531736984854, -74.57376129055876],
        [40.495745325604304, -74.57293784205483],
        [40.496165042187066, -74.57210710302586],
        [40.49657644768055, -74.57126921581468],
        [40.49697947159256, -74.57042432398899],
        [40.497374044866994, -74.56957257231663],
        [40.49776009989578, -74.56871410674087],
        [40.49813757053036, -74.56784907435537],
        [40.49850639209309, -74.56697762337897],
        [40.49886650138829, -74.56609990313032],
        [40.49921783671309, -74.56521606400226],
        [40.49956033786799, -74.56432625743606],
        [40.499893946167184, -74.56343063589553],
        [40.5002186044486, -74.56252935284077],
        [40.500534257083714, -74.56162256270201],
        [40.5401899498965, -74.58504773472853],
        [40.53963755778505, -74.58663461747135],
        [40.53906940579257, -74.58821186281718],
        [40.53848559126899, -74.58977920051312],
        [40.53788621424791, -74.59133636200396],
        [40.53727137742951, -74.59288308047806],
        [40.5366411861629, -74.5944190909132],
        [40.53599574842813, -74.5959441301219],
        [40.53533517481761, -74.59745793679652],
        [40.53465957851725, -74.5989602515541],
        [40.533969075286976, -74.60045081698073],
        [40.53326378344097, -74.60192937767569],
        [40.53254382382737, -74.60339568029524],
        [40.531809319807536, -74.60484947359595],
        [40.53106039723495, -74.60629050847784],
        [40.53029718443365, -74.60771853802699],
        [40.52951981217622, -74.60913331755789],
        [40.528728413661376, -74.61053460465537],
        [40.5279231244912, -74.61192215921606],
        [40.52710408264784, -74.61329574348967],
        [40.52627142846989, -74.61465512211957],
        [40.49258081626851, -74.57854106978262],
    ]

    # Create polygons
    day15_polygon = Polygon([(coord[1], coord[0]) for coord in day_15_coords])
    day18_polygon = Polygon([(coord[1], coord[0]) for coord in day_18_coords])

    # Find intersection
    intersection = day15_polygon.intersection(day18_polygon)

    if not intersection.is_empty and hasattr(intersection, "exterior"):
        print(
            f"\nIntersection found with {len(list(intersection.exterior.coords))} vertices"
        )

        # Get intersection boundary coordinates
        intersection_coords = [
            [coord[1], coord[0]] for coord in intersection.exterior.coords
        ]

        print("\nIntersection boundary coordinates:")
        for i, coord in enumerate(intersection_coords[:10]):  # Show first 10
            print(f"  {i+1:2d}: [{coord[0]:.8f}, {coord[1]:.8f}]")
        if len(intersection_coords) > 10:
            print(f"  ... and {len(intersection_coords)-10} more points")

        # The key insight: find where Day 15 boundary cuts across Day 18
        # Look for coordinates that are on the outer edge of the intersection
        bounds = intersection.bounds  # (minx, miny, maxx, maxy)

        # Find the 4 key corner points
        corners = []

        # Day 18 inner boundary (4-mile mark) - these are our starting points
        corners.append(day18_left_4mile)  # Point 1
        corners.append(day18_right_4mile)  # Point 2

        # Now find where Day 15 cuts Day 18 - look for intersection points that are
        # at the limits of the intersection boundary

        # Find northernmost and southernmost points of intersection
        max_lat = bounds[3]  # North
        min_lat = bounds[1]  # South
        max_lon = bounds[2]  # East
        min_lon = bounds[0]  # West

        # Look for points near these extremes
        tolerance = 0.0001

        extreme_points = []
        for coord in intersection_coords[:-1]:  # Skip last (duplicate of first)
            lat, lon = coord
            if abs(lat - max_lat) < tolerance or abs(lat - min_lat) < tolerance:
                extreme_points.append([lat, lon])
            elif abs(lon - max_lon) < tolerance or abs(lon - min_lon) < tolerance:
                extreme_points.append([lat, lon])

        # Remove duplicates and find the 2 most relevant boundary intersection points
        unique_extremes = []
        for point in extreme_points:
            is_duplicate = False
            for existing in unique_extremes:
                if (
                    abs(point[0] - existing[0]) < tolerance
                    and abs(point[1] - existing[1]) < tolerance
                ):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_extremes.append(point)

        # Add the most relevant boundary points
        if len(unique_extremes) >= 2:
            corners.extend(unique_extremes[:2])

        print(f"\n=== THE 4 CORNER COORDINATES ===")
        for i, corner in enumerate(corners[:4]):
            print(f"{i+1}. [{corner[0]:.8f}, {corner[1]:.8f}]")

        if len(corners) < 4:
            print(
                f"\nOnly found {len(corners)} corners. Let me try a different approach..."
            )

            # Alternative: use the intersection polygon vertices directly
            # Find the 4 vertices that form the corners of the search area
            vertices = intersection_coords[:-1]  # Remove duplicate last point

            if len(vertices) >= 4:
                print("\nUsing intersection vertices as corners:")
                for i in range(min(4, len(vertices))):
                    print(f"{i+1}. [{vertices[i][0]:.8f}, {vertices[i][1]:.8f}]")

    else:
        print("No intersection found or intersection is not a simple polygon")


if __name__ == "__main__":
    main()
