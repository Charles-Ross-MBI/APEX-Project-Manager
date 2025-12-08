"""
Utility for uploading and displaying shapefiles in a Streamlit app.

This module lets users upload zipped shapefiles containing point or polyline geometry.
It extracts the file, reads it with GeoPandas, and displays the geometry on
an interactive Folium map inside Streamlit, with a bottom message bar showing details.
"""

import streamlit as st
import tempfile
import zipfile
from streamlit_folium import st_folium
import folium
import geopandas as gpd
from map import add_small_geocoder, set_bounds_route, add_bottom_message


def point_shapefile():
    st.write("")
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
                coords = gdf.geometry.iloc[0].coords[0]
                lat, lon = coords[1], coords[0]

                # Store selected point in session state
                st.session_state.selected_point = [round(lat, 6), round(lon, 6)]

                # Create map centered on the point
                m = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker([lat, lon], tooltip="Uploaded Point").add_to(m)

                add_small_geocoder(m)
                st_folium(m, width=700, height=500)
            else:
                st.warning("Uploaded shapefile is not point geometry.")


def polyline_shapefile():
    st.write("")
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
                coords = list(gdf.geometry.iloc[0].coords)
                formatted = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]
                st.session_state.selected_route = formatted

                # Create map centered on first coordinate
                m = folium.Map(location=[coords[0][1], coords[0][0]], zoom_start=14)
                folium.PolyLine([(y, x) for x, y in coords], color="blue").add_to(m)

                add_small_geocoder(m)
                m.fit_bounds(set_bounds_route(coords))

                st_folium(m, width=700, height=500)
            else:
                st.warning("Uploaded shapefile is not polyline geometry.")