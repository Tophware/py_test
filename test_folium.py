import folium


# Create a map with both street and satellite views
def create_sample_map():
    # Base map centered on coordinates
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

    # Add street view (default)
    folium.TileLayer("OpenStreetMap", name="Street View").add_to(m)

    # Add satellite view
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add a circle with radius
    folium.Circle(
        location=[40.7128, -74.0060],
        radius=1000,  # 1km radius
        popup="Sample Circle - 1km radius",
        color="red",
        fill=True,
        fillColor="red",
        fillOpacity=0.3,
    ).add_to(m)

    # Add a polygon
    polygon_coords = [
        [40.720, -74.010],
        [40.715, -74.000],
        [40.710, -74.010],
        [40.715, -74.020],
    ]

    folium.Polygon(
        locations=polygon_coords,
        popup="Sample Polygon",
        color="blue",
        fill=True,
        fillColor="blue",
        fillOpacity=0.3,
    ).add_to(m)

    # Add layer control to switch between views
    folium.LayerControl().add_to(m)

    # Save map
    m.save("sample_map.html")
    print("Map saved as 'sample_map.html'")
    print("Open it in your browser to see both street and satellite views!")


if __name__ == "__main__":
    create_sample_map()
