#!/usr/bin/env python3
"""
Find the precise 4 corner coordinates where Day 15 cuts Day 18 wedge
"""

from shapely.geometry import Polygon
import math


def main():
    print("Precise Day 15/Day 18 Wedge Corner Analysis")
    print("=" * 45)

    # Day 15 polygon coordinates (convert to [lon, lat] for Shapely)
    day_15_coords = [
        (-74.78541828511084, 40.43667047680688),
        (-74.78299710693108, 40.43335508327552),
        (-74.78069066107366, 40.42999253486232),
        (-74.77850052826138, 40.42658513609001),
        (-74.77642820950186, 40.4231352222195),
        (-74.77447512505886, 40.41964515764942),
        (-74.7726426134789, 40.416117334295706),
        (-74.77093193067388, 40.41255416995226),
        (-74.76934424906034, 40.40895810663394),
        (-74.76788065675596, 40.40533160890292),
        (-74.76654215683381, 40.40167716217959),
        (-74.76532966663486, 40.3979972710392),
        (-74.76424401713932, 40.39429445749531),
        (-74.76328595239713, 40.39057125927138),
        (-74.76245612901802, 40.38683022806149),
        (-74.76175511572147, 40.38307392778155),
        (-74.76118339294699, 40.379304932812154),
        (-74.7607413525248, 40.37552582623419),
        (-74.76042929740733, 40.37173919805852),
        (-74.76024744146156, 40.36794764345096),
        (-74.76019590932249, 40.36415376095365),
        (-74.47488377330622, 40.363557902384116),
        (-74.4750126036539, 40.3730426086274),
        (-74.47546724351831, 40.3825214951463),
        (-74.47624738131199, 40.391988065585466),
        (-74.47735248236746, 40.401435832030394),
        (-74.47878178930367, 40.41085831945389),
        (-74.48053432254504, 40.42024907015372),
        (-74.48260888099281, 40.42960164817846),
        (-74.48500404284827, 40.43890964373829),
        (-74.48771816658713, 40.448166677598),
        (-74.49074939208452, 40.45736640544898),
        (-74.49409564188991, 40.466502522257294),
        (-74.49775462265085, 40.47556876658485),
        (-74.50172382668468, 40.48455892488065),
        (-74.50600053369723, 40.49346683573926),
        (-74.51058181264713, 40.50228639412355),
        (-74.51546452375463, 40.51101155554874),
        (-74.52064532065344, 40.519636340225034),
        (-74.52612065268416, 40.52815483715581),
        (-74.53188676732769, 40.5365612081888),
        (-74.5379397127771, 40.5448496920172),
    ]

    # Day 18 polygon coordinates (convert to [lon, lat] for Shapely)
    day_18_coords = [
        (-74.57854106978262, 40.49258081626851),
        (-74.57776428199409, 40.493056618655906),
        (-74.5769793766949, 40.4935246425664),
        (-74.57618648837449, 40.4939848078065),
        (-74.57538575289023, 40.494437035529266),
        (-74.57457730744399, 40.4948812482478),
        (-74.57376129055876, 40.49531736984854),
        (-74.57293784205483, 40.495745325604304),
        (-74.57210710302586, 40.496165042187066),
        (-74.57126921581468, 40.49657644768055),
        (-74.57042432398899, 40.49697947159256),
        (-74.56957257231663, 40.497374044866994),
        (-74.56871410674087, 40.49776009989578),
        (-74.56784907435537, 40.49813757053036),
        (-74.56697762337897, 40.49850639209309),
        (-74.56609990313032, 40.49886650138829),
        (-74.56521606400226, 40.49921783671309),
        (-74.56432625743606, 40.49956033786799),
        (-74.56343063589553, 40.499893946167184),
        (-74.56252935284077, 40.5002186044486),
        (-74.56162256270201, 40.500534257083714),
        (-74.58504773472853, 40.5401899498965),
        (-74.58663461747135, 40.53963755778505),
        (-74.58821186281718, 40.53906940579257),
        (-74.58977920051312, 40.53848559126899),
        (-74.59133636200396, 40.53788621424791),
        (-74.59288308047806, 40.53727137742951),
        (-74.5944190909132, 40.5366411861629),
        (-74.5959441301219, 40.53599574842813),
        (-74.59745793679652, 40.53533517481761),
        (-74.5989602515541, 40.53465957851725),
        (-74.60045081698073, 40.533969075286976),
        (-74.60192937767569, 40.53326378344097),
        (-74.60339568029524, 40.53254382382737),
        (-74.60484947359595, 40.531809319807536),
        (-74.60629050847784, 40.53106039723495),
        (-74.60771853802699, 40.53029718443365),
        (-74.60913331755789, 40.52951981217622),
        (-74.61053460465537, 40.528728413661376),
        (-74.61192215921606, 40.5279231244912),
        (-74.61329574348967, 40.52710408264784),
        (-74.61465512211957, 40.52627142846989),
    ]

    # Create polygons
    day15_polygon = Polygon(day_15_coords)
    day18_polygon = Polygon(day_18_coords)

    # Find intersection
    intersection = day15_polygon.intersection(day18_polygon)

    if not intersection.is_empty and hasattr(intersection, "exterior"):
        # Get intersection boundary coordinates (convert back to [lat, lon])
        intersection_coords = [
            (coord[1], coord[0]) for coord in intersection.exterior.coords[:-1]
        ]

        print(f"Intersection has {len(intersection_coords)} vertices")

        # The 4 corners we want are:
        # 1. Day 18 left edge at 4-mile mark (start of Day 18 polygon)
        # 2. Day 18 right edge at 4-mile mark (20th point in Day 18 polygon - before the arc)
        # 3. Where Day 15 boundary intersects Day 18 outer boundary (northernmost point)
        # 4. Where Day 15 boundary intersects Day 18 outer boundary (easternmost point)

        # Day 18 inner boundary points (4-mile mark)
        day18_left_4mile = [
            40.49258081626851,
            -74.57854106978262,
        ]  # First point in Day 18
        day18_right_4mile = [
            40.500534257083714,
            -74.56162256270201,
        ]  # Last inner point in Day 18

        # Find the extreme points of the intersection that represent Day 15 cutting Day 18
        lats = [coord[0] for coord in intersection_coords]
        lons = [coord[1] for coord in intersection_coords]

        max_lat_idx = lats.index(max(lats))
        min_lon_idx = lons.index(min(lons))  # Westernmost (most negative longitude)

        day15_cut_point1 = intersection_coords[max_lat_idx]  # Northernmost intersection
        day15_cut_point2 = intersection_coords[min_lon_idx]  # Westernmost intersection

        print("\n=== THE 4 CORNER COORDINATES ===")
        print(
            "These define the quadrilateral search area where Day 15 cuts into Day 18:"
        )
        print()
        print(
            f"1. Day 18 Left at 4-mile:    [{day18_left_4mile[0]:.8f}, {day18_left_4mile[1]:.8f}]"
        )
        print(
            f"2. Day 18 Right at 4-mile:   [{day18_right_4mile[0]:.8f}, {day18_right_4mile[1]:.8f}]"
        )
        print(
            f"3. Day 15 cuts Day 18 (N):   [{day15_cut_point1[0]:.8f}, {day15_cut_point1[1]:.8f}]"
        )
        print(
            f"4. Day 15 cuts Day 18 (W):   [{day15_cut_point2[0]:.8f}, {day15_cut_point2[1]:.8f}]"
        )

        print(f"\nSearch Area Details:")
        print(f"- This is the area between 4-7 miles from Day 18 center")
        print(f"- Limited by where Day 15 boundary cuts across Day 18 wedge")
        print(f"- Forms a quadrilateral search zone")

        # Calculate approximate area
        from shapely.geometry import Point

        corners = [
            day18_left_4mile,
            day18_right_4mile,
            [day15_cut_point1[0], day15_cut_point1[1]],
            [day15_cut_point2[0], day15_cut_point2[1]],
        ]

        # Convert to lon, lat for Shapely
        corner_polygon = Polygon([(coord[1], coord[0]) for coord in corners])
        area_deg = corner_polygon.area
        area_sq_miles = area_deg * (69 * 69) * 0.78  # Rough conversion at this latitude

        print(f"- Approximate area: {area_sq_miles:.2f} square miles")

    else:
        print("No intersection found")


if __name__ == "__main__":
    main()
