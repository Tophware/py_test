#!/usr/bin/env python3
"""
Enhanced Plot the precise 4-corner search area where Day 15 cuts Day 18 wedge
WITH COMPREHENSIVE PUBLIC AREAS IDENTIFICATION

This enhanced version identifies all public areas within the wedge including:
- Biking trails
- Hiking trails
- Walking trails
- Running trails
- Parks and green spaces
- Recreation facilities
- And all other publicly accessible areas
"""

import folium
import requests
import json
from typing import List, Tuple, Dict, Any
from shapely.geometry import Point, Polygon as ShapelyPolygon
import math


class WedgePublicAreasOverlay:
    """
    Enhanced public areas overlay specifically for the wedge search area.
    Includes comprehensive trail and outdoor activity identification.
    """

    # Overpass API endpoint
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    # Comprehensive color mapping for all outdoor activity types
    AREA_COLORS = {
        "park": {"color": "green", "fillColor": "lightgreen", "icon": "tree"},
        "biking": {"color": "orange", "fillColor": "lightyellow", "icon": "bicycle"},
        "hiking": {"color": "brown", "fillColor": "tan", "icon": "hiking"},
        "walking": {"color": "darkblue", "fillColor": "lightblue", "icon": "walking"},
        "running": {"color": "red", "fillColor": "lightcoral", "icon": "running"},
        "recreation": {
            "color": "blue",
            "fillColor": "lightblue",
            "icon": "football-ball",
        },
        "water": {"color": "cyan", "fillColor": "lightcyan", "icon": "swimmer"},
        "tourism": {"color": "purple", "fillColor": "lavender", "icon": "camera"},
        "education": {
            "color": "darkgreen",
            "fillColor": "lightgreen",
            "icon": "graduation-cap",
        },
        "playground": {"color": "pink", "fillColor": "lightpink", "icon": "child"},
        "fitness": {"color": "maroon", "fillColor": "mistyrose", "icon": "dumbbell"},
        "default": {"color": "gray", "fillColor": "lightgray", "icon": "map-marker"},
    }

    def __init__(self, wedge_corners: List[List[float]]):
        """
        Initialize with the specific wedge coordinates.

        Args:
            wedge_corners: List of [lat, lon] coordinates defining the wedge polygon
        """
        self.wedge_corners = wedge_corners
        self.wedge_polygon = self._create_wedge_polygon()

    def _create_wedge_polygon(self) -> ShapelyPolygon:
        """Create a Shapely polygon from the wedge corners for point-in-polygon testing."""
        # Convert to (lon, lat) format for Shapely (x, y)
        coords = [(corner[1], corner[0]) for corner in self.wedge_corners]
        return ShapelyPolygon(coords)

    def _point_in_wedge(self, lat: float, lon: float) -> bool:
        """Check if a point is inside the wedge polygon."""
        point = Point(lon, lat)  # Shapely uses (x, y) = (lon, lat)
        return self.wedge_polygon.contains(point)

    def get_comprehensive_public_areas(self) -> Dict[str, List[Dict]]:
        """
        Fetch all types of public areas and outdoor activities within the wedge bounds.

        Returns:
            Dictionary with area types as keys and lists of area data as values
        """
        # Calculate bounding box for the wedge
        lats = [corner[0] for corner in self.wedge_corners]
        lons = [corner[1] for corner in self.wedge_corners]

        south, north = min(lats), max(lats)
        west, east = min(lons), max(lons)

        # Add small buffer for edge cases
        buffer = 0.005  # ~500m buffer
        south -= buffer
        north += buffer
        west -= buffer
        east += buffer

        # Comprehensive Overpass query for ALL outdoor and public activities
        query = f"""
        [out:json][timeout:60];
        (
          // Parks and green spaces
          way["leisure"="park"]({south},{west},{north},{east});
          way["leisure"="garden"]({south},{west},{north},{east});
          way["leisure"="nature_reserve"]({south},{west},{north},{east});
          way["landuse"="forest"]({south},{west},{north},{east});
          way["landuse"="recreation_ground"]({south},{west},{north},{east});
          relation["leisure"="park"]({south},{west},{north},{east});
          relation["leisure"="nature_reserve"]({south},{west},{north},{east});
          
          // Biking trails and paths
          way["highway"="cycleway"]({south},{west},{north},{east});
          way["cycleway"]({south},{west},{north},{east});
          way["bicycle"="designated"]({south},{west},{north},{east});
          way["bicycle"="yes"]({south},{west},{north},{east});
          relation["route"="bicycle"]({south},{west},{north},{east});
          
          // Hiking and walking trails
          way["highway"="path"]({south},{west},{north},{east});
          way["highway"="footway"]({south},{west},{north},{east});
          way["highway"="track"]({south},{west},{north},{east});
          way["highway"="bridleway"]({south},{west},{north},{east});
          way["foot"="designated"]({south},{west},{north},{east});
          way["foot"="yes"]({south},{west},{north},{east});
          relation["route"="hiking"]({south},{west},{north},{east});
          relation["route"="foot"]({south},{west},{north},{east});
          
          // Running and fitness trails
          way["sport"="running"]({south},{west},{north},{east});
          way["leisure"="track"]({south},{west},{north},{east});
          way["highway"="track"]["sport"="running"]({south},{west},{north},{east});
          
          // Recreation facilities
          way["leisure"="sports_centre"]({south},{west},{north},{east});
          way["leisure"="playground"]({south},{west},{north},{east});
          way["leisure"="pitch"]({south},{west},{north},{east});
          way["leisure"="golf_course"]({south},{west},{north},{east});
          way["leisure"="swimming_pool"]({south},{west},{north},{east});
          way["leisure"="fitness_centre"]({south},{west},{north},{east});
          way["leisure"="fitness_station"]({south},{west},{north},{east});
          way["amenity"="community_centre"]({south},{west},{north},{east});
          
          // Water features and activities
          way["natural"="water"]({south},{west},{north},{east});
          way["waterway"="river"]({south},{west},{north},{east});
          way["leisure"="marina"]({south},{west},{north},{east});
          way["natural"="beach"]({south},{west},{north},{east});
          
          // Tourism and viewpoints
          way["tourism"="attraction"]({south},{west},{north},{east});
          way["tourism"="viewpoint"]({south},{west},{north},{east});
          way["tourism"="picnic_site"]({south},{west},{north},{east});
          way["tourism"="camp_site"]({south},{west},{north},{east});
          
          // Educational and cultural
          way["amenity"="university"]({south},{west},{north},{east});
          way["amenity"="school"]({south},{west},{north},{east});
          way["amenity"="library"]({south},{west},{north},{east});
          
          // Points of interest (nodes)
          node["leisure"="playground"]({south},{west},{north},{east});
          node["amenity"="bench"]({south},{west},{north},{east});
          node["tourism"="viewpoint"]({south},{west},{north},{east});
          node["natural"="peak"]({south},{west},{north},{east});
          node["leisure"="fitness_station"]({south},{west},{north},{east});
        );
        out geom;
        """

        try:
            print("🔍 Fetching comprehensive public areas data...")
            response = requests.post(self.OVERPASS_URL, data=query, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Organize results by area type and filter by wedge
            results = {
                "park": [],
                "biking": [],
                "hiking": [],
                "walking": [],
                "running": [],
                "recreation": [],
                "water": [],
                "tourism": [],
                "education": [],
                "playground": [],
                "fitness": [],
                "default": [],
            }

            processed_count = 0
            inside_wedge_count = 0

            for element in data.get("elements", []):
                processed_count += 1

                # Check if element is inside the wedge
                if self._element_in_wedge(element):
                    inside_wedge_count += 1
                    area_type = self._classify_comprehensive_area(element)
                    results[area_type].append(element)

            print(
                f"✓ Processed {processed_count} elements, {inside_wedge_count} inside wedge"
            )
            return results

        except Exception as e:
            print(f"❌ Error fetching public areas data: {e}")
            return {
                area_type: []
                for area_type in [
                    "park",
                    "biking",
                    "hiking",
                    "walking",
                    "running",
                    "recreation",
                    "water",
                    "tourism",
                    "education",
                    "playground",
                    "fitness",
                    "default",
                ]
            }

    def _element_in_wedge(self, element: Dict) -> bool:
        """Check if an OSM element is within the wedge polygon."""
        if element["type"] == "node":
            return self._point_in_wedge(element["lat"], element["lon"])
        elif element["type"] == "way" and "geometry" in element:
            # Check if any point of the way is in the wedge
            for node in element["geometry"]:
                if self._point_in_wedge(node["lat"], node["lon"]):
                    return True
        return False

    def _classify_comprehensive_area(self, element: Dict) -> str:
        """
        Classify an OSM element into a specific outdoor activity type.

        Args:
            element: OSM element data

        Returns:
            Area type string
        """
        tags = element.get("tags", {})

        # Biking-specific classification
        if (
            tags.get("highway") == "cycleway"
            or "cycleway" in tags
            or tags.get("bicycle") in ["designated", "yes"]
            or tags.get("route") == "bicycle"
        ):
            return "biking"

        # Running and fitness trails
        elif (
            tags.get("sport") == "running"
            or (tags.get("leisure") == "track" and tags.get("sport") != "motor")
            or tags.get("leisure") == "fitness_station"
            or tags.get("leisure") == "fitness_centre"
        ):
            return "running" if tags.get("sport") == "running" else "fitness"

        # Hiking trails (more specific paths)
        elif (
            tags.get("highway") in ["path", "track", "bridleway"]
            or tags.get("route") == "hiking"
            or (tags.get("foot") == "designated" and tags.get("bicycle") != "yes")
        ):
            return "hiking"

        # Walking paths (general footways)
        elif (
            tags.get("highway") == "footway"
            or tags.get("foot") == "yes"
            or tags.get("route") == "foot"
        ):
            return "walking"

        # Parks and green spaces
        elif tags.get("leisure") in ["park", "garden", "nature_reserve"] or tags.get(
            "landuse"
        ) in ["forest", "recreation_ground"]:
            return "park"

        # Playgrounds specifically
        elif tags.get("leisure") == "playground":
            return "playground"

        # Recreation facilities
        elif (
            tags.get("leisure")
            in ["sports_centre", "pitch", "golf_course", "swimming_pool"]
            or tags.get("amenity") == "community_centre"
        ):
            return "recreation"

        # Water features
        elif (
            tags.get("natural") in ["water", "beach"]
            or tags.get("waterway")
            or tags.get("leisure") == "marina"
        ):
            return "water"

        # Tourism
        elif tags.get("tourism") in [
            "attraction",
            "viewpoint",
            "picnic_site",
            "camp_site",
        ]:
            return "tourism"

        # Education
        elif tags.get("amenity") in ["university", "school", "library"]:
            return "education"

        else:
            return "default"

    def add_to_map(self, map_obj: folium.Map) -> folium.Map:
        """
        Add comprehensive public areas overlay to the map, filtered to wedge area only.

        Args:
            map_obj: Folium map object

        Returns:
            Modified Folium map object
        """
        public_areas = self.get_comprehensive_public_areas()

        # Create feature groups for each area type
        feature_groups = {}
        total_areas = 0

        for area_type, areas in public_areas.items():
            if not areas:
                continue

            total_areas += len(areas)
            colors = self.AREA_COLORS.get(area_type, self.AREA_COLORS["default"])
            feature_group = folium.FeatureGroup(
                name=f"{area_type.title()} ({len(areas)})"
            )

            for area in areas:
                self._add_area_to_group(feature_group, area, area_type, colors)

            feature_groups[area_type] = feature_group
            feature_group.add_to(map_obj)

        print(
            f"🗺️  Added {total_areas} public areas to map across {len(feature_groups)} categories"
        )
        return map_obj

    def _add_area_to_group(
        self,
        feature_group: folium.FeatureGroup,
        area: Dict,
        area_type: str,
        colors: Dict,
    ) -> None:
        """Add a single area to a feature group with enhanced popup information."""
        tags = area.get("tags", {})
        name = tags.get("name", f"Unnamed {area_type}")

        # Create comprehensive popup content
        popup_content = f"<b>{name}</b><br>"
        popup_content += f"🏷️ Type: {area_type.title()}<br>"

        # Add specific activity information
        if area_type == "biking":
            popup_content += "🚴 Biking Trail/Path<br>"
        elif area_type == "hiking":
            popup_content += "🥾 Hiking Trail<br>"
        elif area_type == "walking":
            popup_content += "🚶 Walking Path<br>"
        elif area_type == "running":
            popup_content += "🏃 Running Track/Trail<br>"
        elif area_type == "fitness":
            popup_content += "💪 Fitness Station/Gym<br>"

        # Add relevant tag information
        relevant_tags = [
            "surface",
            "difficulty",
            "length",
            "operator",
            "opening_hours",
            "website",
            "phone",
        ]
        for tag in relevant_tags:
            if tag in tags:
                popup_content += f"{tag.title()}: {tags[tag]}<br>"

        # Add coordinates for reference
        if area["type"] == "node":
            popup_content += f"📍 {area['lat']:.6f}, {area['lon']:.6f}"

        if area["type"] == "way" and "geometry" in area:
            # Handle way geometries (polygons and lines)
            coordinates = [[node["lat"], node["lon"]] for node in area["geometry"]]

            if len(coordinates) > 2 and coordinates[0] == coordinates[-1]:
                # Closed way (polygon)
                folium.Polygon(
                    locations=coordinates,
                    popup=popup_content,
                    tooltip=name,
                    color=colors["color"],
                    weight=2,
                    fill=True,
                    fillColor=colors["fillColor"],
                    fillOpacity=0.4,
                ).add_to(feature_group)
            else:
                # Open way (line) - make trails more visible
                weight = (
                    4 if area_type in ["biking", "hiking", "walking", "running"] else 3
                )
                folium.PolyLine(
                    locations=coordinates,
                    popup=popup_content,
                    tooltip=name,
                    color=colors["color"],
                    weight=weight,
                    opacity=0.8,
                ).add_to(feature_group)

        elif area["type"] == "node":
            # Handle node geometries (points)
            folium.Marker(
                location=[area["lat"], area["lon"]],
                popup=popup_content,
                tooltip=name,
                icon=folium.Icon(
                    color=colors["color"], icon=colors["icon"], prefix="fa"
                ),
            ).add_to(feature_group)


def main():
    print("🎯 ENHANCED Day 15/Day 18 Wedge Search Area with Comprehensive Public Areas")
    print("=" * 80)

    # The 4 precise corner coordinates
    corners = [
        [40.49258082, -74.57854107],  # Day 18 Left at 4-mile
        [40.50053426, -74.56162256],  # Day 18 Right at 4-mile
        [40.52752728, -74.57756772],  # Day 15 cuts Day 18 (North)
        [40.51608736, -74.60373849],  # Day 15 cuts Day 18 (West)
    ]

    corner_labels = [
        "Day 18 Left (4-mile)",
        "Day 18 Right (4-mile)",
        "Day 15 cuts Day 18 (N)",
        "Day 15 cuts Day 18 (W)",
    ]

    # Calculate center for map
    center_lat = sum(coord[0] for coord in corners) / len(corners)
    center_lon = sum(coord[1] for coord in corners) / len(corners)

    # Create enhanced map with multiple tile options
    search_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add multiple tile layers for different views
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(search_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(search_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topographic View",
        overlay=False,
        control=True,
    ).add_to(search_map)

    # Initialize and add comprehensive public areas overlay
    print("🌲 Initializing comprehensive public areas detection...")
    try:
        # Install shapely if not available
        try:
            from shapely.geometry import Point, Polygon as ShapelyPolygon
        except ImportError:
            print("⚠️  Shapely not installed. Installing...")
            import subprocess
            import sys

            subprocess.check_call([sys.executable, "-m", "pip", "install", "shapely"])
            from shapely.geometry import Point, Polygon as ShapelyPolygon

        public_areas_overlay = WedgePublicAreasOverlay(corners)
        search_map = public_areas_overlay.add_to_map(search_map)

    except Exception as e:
        print(f"⚠️  Could not add public areas overlay: {e}")
        print("Continuing with basic map...")

    # Add corner markers
    colors = ["red", "blue", "green", "purple"]
    for i, (coord, label, color) in enumerate(zip(corners, corner_labels, colors)):
        folium.Marker(
            location=coord,
            popup=f"<b>Corner {i+1}: {label}</b><br>Lat: {coord[0]:.8f}<br>Lon: {coord[1]:.8f}",
            tooltip=f"Corner {i+1}: {label}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(search_map)

    # Create the search quadrilateral
    quad_coords = [
        corners[0],  # Day 18 Left (4-mile)
        corners[1],  # Day 18 Right (4-mile)
        corners[2],  # Day 15 cuts Day 18 (N)
        corners[3],  # Day 15 cuts Day 18 (W)
        corners[0],  # Close the polygon
    ]

    folium.Polygon(
        locations=quad_coords,
        color="orange",
        weight=4,
        fillColor="yellow",
        fillOpacity=0.2,
        popup="<b>SEARCH AREA</b><br>Day 15/Day 18 Overlap<br>~2.76 square miles<br>📍 All public areas shown are within this wedge!",
        tooltip="Primary Search Area Wedge",
    ).add_to(search_map)

    # Add center points for reference
    day18_center = [40.44766, -74.530389]
    day15_center = [40.364551, -74.950404]

    folium.Marker(
        location=day18_center,
        popup="<b>Day 18 Center</b><br>(High Voltage Lines)",
        tooltip="Day 18 Center",
        icon=folium.Icon(color="darkgreen", icon="flash"),
    ).add_to(search_map)

    folium.Marker(
        location=day15_center,
        popup="<b>Day 15 Center</b><br>(New Hope Bridge)",
        tooltip="Day 15 Center",
        icon=folium.Icon(color="darkblue", icon="home"),
    ).add_to(search_map)

    # Add layer control
    folium.LayerControl().add_to(search_map)

    # Save enhanced map
    output_file = "enhanced_wedge_search_with_public_areas.html"
    search_map.save(output_file)

    print(f"\n🗺️  Enhanced search area map saved as: {output_file}")
    print("\n=== WEDGE COORDINATES ===")
    for i, (coord, label) in enumerate(zip(corners, corner_labels)):
        print(f"{i+1}. {label:20}: [{coord[0]:.8f}, {coord[1]:.8f}]")

    print(f"\n🎯 Search Area Details:")
    print(f"   📏 Area: ~2.76 square miles")
    print(f"   📍 Between 4-7 miles from Day 18 center")
    print(f"   🔶 Yellow highlighted quadrilateral on the map")

    print(f"\n🏃 Public Areas Identified WITHIN WEDGE:")
    print(f"   🚴 Biking trails and cycle paths")
    print(f"   🥾 Hiking trails and nature paths")
    print(f"   🚶 Walking paths and footways")
    print(f"   🏃 Running tracks and fitness trails")
    print(f"   🌳 Parks and green spaces")
    print(f"   ⚽ Recreation facilities and sports areas")
    print(f"   💧 Water features and swimming areas")
    print(f"   🏛️ Tourism attractions and viewpoints")
    print(f"   🎓 Educational facilities")
    print(f"   🎪 Playgrounds and family areas")
    print(f"   💪 Fitness stations and outdoor gyms")

    print(f"\n💡 Map Features:")
    print(f"   • Layer control (top-right) for Street/Satellite/Topo views")
    print(f"   • Color-coded areas by activity type")
    print(f"   • Click any area/trail for detailed information")
    print(f"   • Only shows public areas INSIDE the search wedge")

    return search_map


if __name__ == "__main__":
    main()
