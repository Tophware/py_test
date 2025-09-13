import folium
import math
from main import create_sector_polygon


def create_interactive_rotation_map():
    """
    Creates an interactive map with browser-based rotation controls for the sector polygon.
    """
    # Day 15 coordinates
    start_lat, start_lon = 40.364551, -74.950404
    direction_lat, direction_lon = 40.365207, -74.947155

    # Create base map
    m = folium.Map(location=[start_lat, start_lon], zoom_start=11)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add center marker
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Day 15 - New Hope Bridge (Interactive Rotation Center)",
        tooltip="Rotation Center - Use controls to rotate sector",
        icon=folium.Icon(color="red", icon="star"),
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Get the HTML representation
    map_html = m._repr_html_()

    # Create custom HTML with JavaScript controls
    interactive_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Interactive Sector Rotation - Day 15</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 85vh;
            width: 100%;
        }}
        .controls {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            min-width: 250px;
        }}
        .control-group {{
            margin-bottom: 12px;
        }}
        .control-group label {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        .button-group {{
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
        }}
        button {{
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.2s;
        }}
        .rotate-btn {{
            background: #4CAF50;
            color: white;
            flex: 1;
        }}
        .rotate-btn:hover {{
            background: #45a049;
        }}
        .reset-btn {{
            background: #f44336;
            color: white;
            width: 100%;
        }}
        .reset-btn:hover {{
            background: #da190b;
        }}
        .fine-btn {{
            background: #2196F3;
            color: white;
            flex: 1;
        }}
        .fine-btn:hover {{
            background: #1976D2;
        }}
        .angle-display {{
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid #ddd;
        }}
        .instructions {{
            font-size: 12px;
            color: #666;
            margin-top: 10px;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="controls">
        <div class="control-group">
            <label>🎯 Sector Rotation Controls</label>
            <div class="button-group">
                <button class="rotate-btn" onclick="rotateSector(-15)">↺ 15° CCW</button>
                <button class="rotate-btn" onclick="rotateSector(15)">↻ 15° CW</button>
            </div>
            <div class="button-group">
                <button class="fine-btn" onclick="rotateSector(-5)">↺ 5° CCW</button>
                <button class="fine-btn" onclick="rotateSector(5)">↻ 5° CW</button>
            </div>
            <button class="reset-btn" onclick="resetRotation()">🔄 Reset to Original</button>
        </div>
        
        <div class="control-group">
            <label>Current Rotation:</label>
            <div class="angle-display" id="angle-display">0°</div>
        </div>
        
        <div class="instructions">
            Use the buttons above to rotate the Day 15 search sector around the New Hope Bridge center point. 
            The sector shows a 10-25 mile range with 30° width.
        </div>
    </div>

    <script>
        // Initialize map
        var map = L.map('map').setView([{start_lat}, {start_lon}], 11);
        
        // Add tile layers
        var streetLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }});
        
        var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Esri'
        }});
        
        // Add default layer
        satelliteLayer.addTo(map);
        
        // Layer control
        var baseMaps = {{
            "Street View": streetLayer,
            "Satellite View": satelliteLayer
        }};
        L.control.layers(baseMaps).addTo(map);
        
        // Add center marker
        var centerMarker = L.marker([{start_lat}, {start_lon}])
            .addTo(map)
            .bindPopup("Day 15 - New Hope Bridge<br>Interactive Rotation Center")
            .bindTooltip("Rotation Center - Use controls to rotate sector");
        
        // Sector parameters
        var centerLat = {start_lat};
        var centerLon = {start_lon};
        var bearingLat = {direction_lat};
        var bearingLon = {direction_lon};
        var widthDegrees = 30;
        var minRadiusMiles = 10;
        var maxRadiusMiles = 25;
        var currentRotation = 0;
        
        // Current sector polygon and reference lines
        var sectorPolygon = null;
        var centerLine = null;
        var leftBoundaryLine = null;
        var rightBoundaryLine = null;
        
        // Calculate bearing between two points
        function calculateBearing(lat1, lon1, lat2, lon2) {{
            var dLon = (lon2 - lon1) * Math.PI / 180;
            var lat1Rad = lat1 * Math.PI / 180;
            var lat2Rad = lat2 * Math.PI / 180;
            
            var y = Math.sin(dLon) * Math.cos(lat2Rad);
            var x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
            
            return Math.atan2(y, x);
        }}
        
        // Create reference line coordinates
        function createReferenceLines(rotationDegrees) {{
            var bearingCenter = calculateBearing(centerLat, centerLon, bearingLat, bearingLon);
            bearingCenter += rotationDegrees * Math.PI / 180; // Apply rotation
            
            var halfWidth = widthDegrees * Math.PI / 360; // Convert to radians and halve
            var bearingLeft = bearingCenter - halfWidth;
            var bearingRight = bearingCenter + halfWidth;
            
            var minRadiusDeg = minRadiusMiles / 69.0;
            var maxRadiusDeg = maxRadiusMiles / 69.0;
            
            // Center line (extends through entire sector)
            var centerLineStart = [
                centerLat + maxRadiusDeg * Math.cos(bearingCenter),
                centerLon + maxRadiusDeg * Math.sin(bearingCenter) / Math.cos(centerLat * Math.PI / 180)
            ];
            var centerLineEnd = [centerLat, centerLon];
            
            // Left boundary line (from center to min radius)
            var leftLineStart = [centerLat, centerLon];
            var leftLineEnd = [
                centerLat + minRadiusDeg * Math.cos(bearingLeft),
                centerLon + minRadiusDeg * Math.sin(bearingLeft) / Math.cos(centerLat * Math.PI / 180)
            ];
            
            // Right boundary line (from center to min radius)
            var rightLineStart = [centerLat, centerLon];
            var rightLineEnd = [
                centerLat + minRadiusDeg * Math.cos(bearingRight),
                centerLon + minRadiusDeg * Math.sin(bearingRight) / Math.cos(centerLat * Math.PI / 180)
            ];
            
            return {{
                center: [centerLineEnd, centerLineStart],
                left: [leftLineStart, leftLineEnd],
                right: [rightLineStart, rightLineEnd]
            }};
        }}
        
        // Create sector polygon coordinates
        function createSectorCoordinates(rotationDegrees) {{
            var bearingCenter = calculateBearing(centerLat, centerLon, bearingLat, bearingLon);
            bearingCenter += rotationDegrees * Math.PI / 180; // Apply rotation
            
            var halfWidth = widthDegrees * Math.PI / 360; // Convert to radians and halve
            var bearingLeft = bearingCenter - halfWidth;
            var bearingRight = bearingCenter + halfWidth;
            
            var minRadiusDeg = minRadiusMiles / 69.0;
            var maxRadiusDeg = maxRadiusMiles / 69.0;
            
            var coords = [];
            
            // Arc along minimum radius from left to right
            var numArcPoints = 20;
            for (var i = 0; i <= numArcPoints; i++) {{
                var bearing = bearingLeft + (bearingRight - bearingLeft) * i / numArcPoints;
                var lat = centerLat + minRadiusDeg * Math.cos(bearing);
                var lon = centerLon + minRadiusDeg * Math.sin(bearing) / Math.cos(centerLat * Math.PI / 180);
                coords.push([lat, lon]);
            }}
            
            // Arc along maximum radius from right to left
            for (var i = 0; i <= numArcPoints; i++) {{
                var bearing = bearingRight - (bearingRight - bearingLeft) * i / numArcPoints;
                var lat = centerLat + maxRadiusDeg * Math.cos(bearing);
                var lon = centerLon + maxRadiusDeg * Math.sin(bearing) / Math.cos(centerLat * Math.PI / 180);
                coords.push([lat, lon]);
            }}
            
            // Close polygon back to start of min radius arc (no center point)
            var bearing = bearingLeft;
            var lat = centerLat + minRadiusDeg * Math.cos(bearing);
            var lon = centerLon + minRadiusDeg * Math.sin(bearing) / Math.cos(centerLat * Math.PI / 180);
            coords.push([lat, lon]);
            
            return coords;
        }}
        
        // Update sector display
        function updateSector() {{
            // Remove existing sector and lines
            if (sectorPolygon) {{
                map.removeLayer(sectorPolygon);
            }}
            if (centerLine) {{
                map.removeLayer(centerLine);
            }}
            if (leftBoundaryLine) {{
                map.removeLayer(leftBoundaryLine);
            }}
            if (rightBoundaryLine) {{
                map.removeLayer(rightBoundaryLine);
            }}
            
            // Create new sector
            var coords = createSectorCoordinates(currentRotation);
            sectorPolygon = L.polygon(coords, {{
                color: 'blue',
                weight: 2,
                fillColor: 'lightblue',
                fillOpacity: 0.4
            }}).addTo(map);
            
            sectorPolygon.bindPopup(`Day 15 Search Sector<br>Rotation: ${{currentRotation}}°<br>Range: ${{minRadiusMiles}}-${{maxRadiusMiles}} miles`);
            
            // Create reference lines
            var refLines = createReferenceLines(currentRotation);
            
            // Center bearing line (dashed, extends through center)
            centerLine = L.polyline(refLines.center, {{
                color: 'red',
                weight: 2,
                dashArray: '8, 8',
                opacity: 0.8
            }}).addTo(map);
            centerLine.bindTooltip("Center Bearing Line");
            
            // Left boundary line (dashed, center to min radius)
            leftBoundaryLine = L.polyline(refLines.left, {{
                color: 'purple',
                weight: 2,
                dashArray: '6, 6',
                opacity: 0.8
            }}).addTo(map);
            leftBoundaryLine.bindTooltip("Left Boundary (-15°) - Center to Min Radius");
            
            // Right boundary line (dashed, center to min radius)
            rightBoundaryLine = L.polyline(refLines.right, {{
                color: 'purple',
                weight: 2,
                dashArray: '6, 6',
                opacity: 0.8
            }}).addTo(map);
            rightBoundaryLine.bindTooltip("Right Boundary (+15°) - Center to Min Radius");
            
            // Update angle display
            document.getElementById('angle-display').textContent = currentRotation + '°';
        }}
        
        // Rotate sector
        function rotateSector(degrees) {{
            currentRotation += degrees;
            // Keep rotation between -360 and 360
            if (currentRotation > 360) currentRotation -= 360;
            if (currentRotation < -360) currentRotation += 360;
            updateSector();
        }}
        
        // Reset rotation
        function resetRotation() {{
            currentRotation = 0;
            updateSector();
        }}
        
        // Initialize with original sector
        updateSector();
        
        // Add keyboard controls
        document.addEventListener('keydown', function(event) {{
            switch(event.key) {{
                case 'ArrowLeft':
                    rotateSector(-5);
                    event.preventDefault();
                    break;
                case 'ArrowRight':
                    rotateSector(5);
                    event.preventDefault();
                    break;
                case 'r':
                case 'R':
                    resetRotation();
                    event.preventDefault();
                    break;
            }}
        }});
        
        console.log("Interactive rotation controls loaded!");
        console.log("Use arrow keys for 5° rotation, or R to reset");
    </script>
</body>
</html>
"""

    # Save the interactive map
    filename = "interactive_sector_rotation.html"
    with open(filename, "w") as f:
        f.write(interactive_html)

    print(f"Interactive rotation map created: {filename}")
    print("🎯 Controls available:")
    print("  • Buttons: 15° and 5° rotation (CW/CCW)")
    print("  • Reset button to return to original bearing")
    print("  • Keyboard: Arrow keys (5°), R key (reset)")
    print("  • Real-time angle display")

    return filename


if __name__ == "__main__":
    create_interactive_rotation_map()
