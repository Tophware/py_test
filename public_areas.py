"""
Public Areas Overlay Module

This module provides functionality to identify and display public areas such as parks,
hiking trails, recreational facilities, and other publicly accessible spaces on a map
using OpenStreetMap data via the Overpass API.
"""

import requests
import folium
import json
from typing import List, Dict, Tuple, Optional, Any


class PublicAreasOverlay:
    """
    A class to handle identification and visualization of public areas on maps.
    """

    # Overpass API endpoint
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    # Color mapping for different types of public areas
    AREA_COLORS = {
        "park": {"color": "green", "fillColor": "lightgreen", "icon": "tree"},
        "hiking": {"color": "brown", "fillColor": "tan", "icon": "shoe-prints"},
        "recreation": {"color": "blue", "fillColor": "lightblue", "icon": "gamepad"},
        "beach": {
            "color": "yellow",
            "fillColor": "lightyellow",
            "icon": "umbrella-beach",
        },
        "water": {"color": "cyan", "fillColor": "lightcyan", "icon": "swimmer"},
        "tourism": {"color": "purple", "fillColor": "lavender", "icon": "camera"},
        "education": {
            "color": "orange",
            "fillColor": "lightyellow",
            "icon": "graduation-cap",
        },
        "cemetery": {"color": "gray", "fillColor": "lightgray", "icon": "cross"},
        "default": {
            "color": "darkgreen",
            "fillColor": "lightgreen",
            "icon": "map-marker",
        },
    }

    def __init__(self):
        """Initialize the PublicAreasOverlay."""
        pass

    def get_public_areas(
        self,
        bounds: Tuple[float, float, float, float],
        area_types: Optional[List[str]] = None,
    ) -> Dict[str, List[dict]]:
        """
        Fetch public areas within the specified bounds using Overpass API.

        Args:
            bounds: Tuple of (south, west, north, east) coordinates
            area_types: List of area types to fetch. If None, fetches all types.

        Returns:
            Dictionary with area types as keys and lists of area data as values
        """
        if area_types is None:
            area_types = [
                "park",
                "hiking",
                "recreation",
                "beach",
                "water",
                "tourism",
                "education",
            ]

        south, west, north, east = bounds

        # Build Overpass query for different public area types
        query_parts = []

        # Parks and green spaces
        if "park" in area_types:
            query_parts.extend(
                [
                    f'way["leisure"="park"]({south},{west},{north},{east});',
                    f'way["leisure"="garden"]({south},{west},{north},{east});',
                    f'way["leisure"="nature_reserve"]({south},{west},{north},{east});',
                    f'way["landuse"="forest"]({south},{west},{north},{east});',
                    f'way["landuse"="recreation_ground"]({south},{west},{north},{east});',
                    f'relation["leisure"="park"]({south},{west},{north},{east});',
                    f'relation["leisure"="nature_reserve"]({south},{west},{north},{east});',
                ]
            )

        # Hiking and trails
        if "hiking" in area_types:
            query_parts.extend(
                [
                    f'way["highway"="path"]({south},{west},{north},{east});',
                    f'way["highway"="footway"]({south},{west},{north},{east});',
                    f'way["highway"="track"]({south},{west},{north},{east});',
                    f'way["route"="hiking"]({south},{west},{north},{east});',
                    f'relation["route"="hiking"]({south},{west},{north},{east});',
                ]
            )

        # Recreation facilities
        if "recreation" in area_types:
            query_parts.extend(
                [
                    f'way["leisure"="sports_centre"]({south},{west},{north},{east});',
                    f'way["leisure"="playground"]({south},{west},{north},{east});',
                    f'way["leisure"="pitch"]({south},{west},{north},{east});',
                    f'way["leisure"="golf_course"]({south},{west},{north},{east});',
                    f'way["leisure"="swimming_pool"]({south},{west},{north},{east});',
                    f'way["amenity"="community_centre"]({south},{west},{north},{east});',
                ]
            )

        # Beach areas
        if "beach" in area_types:
            query_parts.extend(
                [
                    f'way["leisure"="beach_resort"]({south},{west},{north},{east});',
                    f'way["natural"="beach"]({south},{west},{north},{east});',
                ]
            )

        # Water areas
        if "water" in area_types:
            query_parts.extend(
                [
                    f'way["natural"="water"]({south},{west},{north},{east});',
                    f'way["waterway"="river"]({south},{west},{north},{east});',
                    f'way["leisure"="marina"]({south},{west},{north},{east});',
                ]
            )

        # Tourism
        if "tourism" in area_types:
            query_parts.extend(
                [
                    f'way["tourism"="attraction"]({south},{west},{north},{east});',
                    f'way["tourism"="viewpoint"]({south},{west},{north},{east});',
                    f'way["tourism"="picnic_site"]({south},{west},{north},{east});',
                    f'way["tourism"="camp_site"]({south},{west},{north},{east});',
                ]
            )

        # Educational facilities
        if "education" in area_types:
            query_parts.extend(
                [
                    f'way["amenity"="university"]({south},{west},{north},{east});',
                    f'way["amenity"="school"]({south},{west},{north},{east});',
                    f'way["amenity"="library"]({south},{west},{north},{east});',
                ]
            )

        # Construct full query
        query = f"""
        [out:json][timeout:25];
        (
          {chr(10).join(query_parts)}
        );
        out geom;
        """

        try:
            response = requests.post(self.OVERPASS_URL, data=query, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Organize results by area type
            results = {area_type: [] for area_type in area_types}

            for element in data.get("elements", []):
                area_type = self._classify_area(element)
                if area_type in results:
                    results[area_type].append(element)

            return results

        except Exception as e:
            print(f"Error fetching public areas data: {e}")
            return {area_type: [] for area_type in area_types}

    def _classify_area(self, element: dict) -> str:
        """
        Classify an OSM element into a public area type.

        Args:
            element: OSM element data

        Returns:
            Area type string
        """
        tags = element.get("tags", {})

        # Check various tag combinations to classify the area
        if tags.get("leisure") in ["park", "garden", "nature_reserve"] or tags.get(
            "landuse"
        ) in ["forest", "recreation_ground"]:
            return "park"
        elif (
            tags.get("highway") in ["path", "footway", "track"]
            or tags.get("route") == "hiking"
        ):
            return "hiking"
        elif (
            tags.get("leisure")
            in ["sports_centre", "playground", "pitch", "golf_course", "swimming_pool"]
            or tags.get("amenity") == "community_centre"
        ):
            return "recreation"
        elif tags.get("leisure") == "beach_resort" or tags.get("natural") == "beach":
            return "beach"
        elif (
            tags.get("natural") == "water"
            or tags.get("waterway")
            or tags.get("leisure") == "marina"
        ):
            return "water"
        elif tags.get("tourism") in [
            "attraction",
            "viewpoint",
            "picnic_site",
            "camp_site",
        ]:
            return "tourism"
        elif tags.get("amenity") in ["university", "school", "library"]:
            return "education"
        elif tags.get("landuse") == "cemetery":
            return "cemetery"
        else:
            return "default"

    def add_public_areas_to_map(
        self,
        map_obj: folium.Map,
        bounds: Tuple[float, float, float, float],
        area_types: Optional[List[str]] = None,
        enabled_types: Optional[List[str]] = None,
    ) -> folium.Map:
        """
        Add public areas overlay to a Folium map.

        Args:
            map_obj: Folium map object
            bounds: Tuple of (south, west, north, east) coordinates
            area_types: List of area types to fetch
            enabled_types: List of area types to display (subset of area_types)

        Returns:
            Modified Folium map object
        """
        public_areas = self.get_public_areas(bounds, area_types)

        if enabled_types is None:
            enabled_types = list(public_areas.keys())

        # Create feature groups for each area type
        feature_groups = {}

        for area_type, areas in public_areas.items():
            if area_type not in enabled_types or not areas:
                continue

            colors = self.AREA_COLORS.get(area_type, self.AREA_COLORS["default"])
            feature_group = folium.FeatureGroup(
                name=f"Public {area_type.title()} Areas"
            )

            for area in areas:
                self._add_area_to_group(feature_group, area, area_type, colors)

            feature_groups[area_type] = feature_group
            feature_group.add_to(map_obj)

        return map_obj

    def _add_area_to_group(
        self,
        feature_group: folium.FeatureGroup,
        area: dict,
        area_type: str,
        colors: dict,
    ) -> None:
        """
        Add a single area to a feature group.

        Args:
            feature_group: Folium feature group
            area: OSM area data
            area_type: Type of area
            colors: Color configuration for the area type
        """
        tags = area.get("tags", {})
        name = tags.get("name", f"Unnamed {area_type}")

        # Create popup content
        popup_content = f"<b>{name}</b><br>"
        popup_content += f"Type: {area_type.title()}<br>"

        # Add relevant tag information
        relevant_tags = ["operator", "opening_hours", "website", "phone", "description"]
        for tag in relevant_tags:
            if tag in tags:
                popup_content += f"{tag.title()}: {tags[tag]}<br>"

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
                    fillOpacity=0.3,
                ).add_to(feature_group)
            else:
                # Open way (line)
                folium.PolyLine(
                    locations=coordinates,
                    popup=popup_content,
                    tooltip=name,
                    color=colors["color"],
                    weight=3,
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

    @staticmethod
    def calculate_bounds_from_sectors(
        sector_datasets: List[dict], padding_miles: float = 5
    ) -> Tuple[float, float, float, float]:
        """
        Calculate bounding box from sector datasets with optional padding.

        Args:
            sector_datasets: List of sector configuration dictionaries
            padding_miles: Additional padding in miles around the sectors

        Returns:
            Tuple of (south, west, north, east) coordinates
        """
        if not sector_datasets:
            return (40.0, -75.0, 41.0, -74.0)  # Default bounds for NJ/NY area

        # Extract all coordinates from enabled sectors
        lats = []
        lons = []

        for sector in sector_datasets:
            if sector.get("enabled", True):
                lats.extend([sector["center_lat"], sector["bearing_lat"]])
                lons.extend([sector["center_lon"], sector["bearing_lon"]])

        if not lats:
            return (40.0, -75.0, 41.0, -74.0)

        # Calculate bounds with padding (approximate: 1 degree ≈ 69 miles)
        padding_deg = padding_miles / 69.0

        south = min(lats) - padding_deg
        north = max(lats) + padding_deg
        west = min(lons) - padding_deg
        east = max(lons) + padding_deg

        return (south, west, north, east)


def create_public_areas_demo():
    """
    Create a demonstration map showing public areas overlay functionality.
    """
    # Initialize the overlay
    overlay = PublicAreasOverlay()

    # Example bounds around central New Jersey
    bounds = (40.0, -75.0, 41.0, -74.0)  # (south, west, north, east)

    # Create base map
    center_lat = (bounds[0] + bounds[2]) / 2
    center_lon = (bounds[1] + bounds[3]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Add tile layers
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add public areas overlay
    m = overlay.add_public_areas_to_map(m, bounds)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the demo map
    demo_map_name = "public_areas_demo.html"
    m.save(demo_map_name)

    print(f"Public areas demonstration map saved as '{demo_map_name}'")
    print("The map includes overlays for:")
    print("  • Parks and green spaces")
    print("  • Hiking trails and paths")
    print("  • Recreation facilities")
    print("  • Tourism attractions")
    print("  • Educational facilities")
    print("  • Water features")

    return m


if __name__ == "__main__":
    create_public_areas_demo()
