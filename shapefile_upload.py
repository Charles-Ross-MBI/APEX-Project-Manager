"""
Utility for uploading and displaying point shapefiles in a Streamlit app.

This module lets users upload a zipped shapefile containing point geometry.
It extracts the file, reads it with GeoPandas, and displays the point on
an interactive Folium map inside Streamlit.
"""

import streamlit as st
import tempfile
import zipfile
from streamlit_folium import st_folium
import folium
import geopandas as gpd
from map import add_small_geocoder
from map import set_bounds_route


def point_shapefile():
    st.write("")
    """
    Upload a zipped point shapefile and display it on a Folium map.

    - Prompts the user to upload a `.zip` file containing shapefile components.
    - Extracts and reads the shapefile using GeoPandas.
    - If geometry is a Point, places a marker on a Folium map.
    - If geometry is not a Point, still shows a map but warns the user.
    - Adds a small geocoder control for searching locations.
    - Renders the map in Streamlit.
    """
    uploaded = st.file_uploader("Upload point shapefile (zip)", type=["zip"])
        
    if uploaded:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = f"{tmpdir}/shapefile.zip"

            with open(zip_path, "wb") as f:
                f.write(uploaded.getbuffer())

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            gdf = gpd.read_file(tmpdir)

            if gdf.geom_type.iloc[0] == "Point":
                # Extract coordinates (lon, lat)
                coords = gdf.geometry.iloc[0].coords[0]
                lat, lon = coords[1], coords[0]

                # ✅ Store selected point in Streamlit session state as [lat, lon]
                st.session_state.selected_point = [round(lat, 6), round(lon, 6)]

                # Create Folium map centered on the point
                m = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker([lat, lon], popup="Uploaded Point").add_to(m)
                add_small_geocoder(m)
                st_folium(m, width=700, height=500)
                st.success(f"Point Loaded: [{round(lat,6)}, {round(lon,6)}]")

            else:
                st.warning("Uploaded shapefile is not point geometry.")



def polyline_shapefile():
    st.write("")
    """
    Upload a zipped polyline shapefile and display it on a Folium map.

    - Prompts the user to upload a `.zip` file containing shapefile components.
    - Extracts and reads the shapefile using GeoPandas.
    - If geometry is a LineString, draws the polyline on a Folium map.
    - If geometry is not a LineString, still shows a map but warns the user.
    - Adds a small geocoder control for searching locations.
    - Renders the map in Streamlit.
    """
    uploaded = st.file_uploader("Upload polyline shapefile (zip)", type=["zip"])

    if uploaded:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = f"{tmpdir}/shapefile.zip"

            with open(zip_path, "wb") as f:
                f.write(uploaded.getbuffer())

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            gdf = gpd.read_file(tmpdir)

            if gdf.geom_type.iloc[0] == "LineString":
                # Extract coordinates from the line
                coords = list(gdf.geometry.iloc[0].coords)  # [(lon, lat), ...]

                # ✅ Store consistently as [lat, lon] pairs
                formatted = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]
                st.session_state.selected_route = formatted

                # Create Folium map centered on the first coordinate
                m = folium.Map(location=[coords[0][1], coords[0][0]], zoom_start=14)

                # Draw polyline on the map (convert coords to lat/lon order)
                folium.PolyLine([(y, x) for x, y in coords], color="blue").add_to(m)

                add_small_geocoder(m)

                # Fit bounds to route
                m.fit_bounds(set_bounds_route(coords))

                st_folium(m, width=700, height=500)

                st.success(f"Route Loaded from Shapefile with {len(formatted)} points")
            else:
                st.warning("Uploaded shapefile is not polyline geometry.")

