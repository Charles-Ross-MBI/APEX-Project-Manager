"""
Streamlit functions for drawing points and lines on a Folium map.

Users can interactively draw geometries, which are then stored
in Streamlit session state and displayed with success messages.
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw, Geocoder
from map import add_small_geocoder


def draw_point():
    st.write("")
    """
    Display a Folium map where the user can draw a point.

    - Map centered on Alaska.
    - Only marker drawing tool enabled.
    - Captures last drawn point and saves to session state.
    """
    # Create map centered on Alaska
    m = folium.Map(location=[64.0000, -152.0000], zoom_start=4)

    # Enable only marker drawing
    draw = Draw(
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "rectangle": False,
            "circlemarker": False,
            "marker": True,
        },
        edit_options={"edit": True}
    )
    draw.add_to(m)

    # Add geocoder control
    add_small_geocoder(m)

    # Render map in Streamlit
    output = st_folium(m, width=700, height=500)

    # If a point was drawn, save coordinates
    if output and "all_drawings" in output and output["all_drawings"]:
        last = output["all_drawings"][-1]
        if last["geometry"]["type"] == "Point":
            coords = last["geometry"]["coordinates"]  # [lon, lat]
            lon, lat = coords[0], coords[1]

            # ✅ Store consistently as [lat, lon]
            st.session_state.selected_point = [round(lat, 6), round(lon, 6)]

            # Optional confirmation message
            st.success(f"Point Loaded: [{round(lat,6)}, {round(lon,6)}]")


def draw_line():
    st.write("")
    """
    Display a Folium map where the user can draw a line.

    - Map centered on Alaska.
    - Only polyline drawing tool enabled.
    - Captures last drawn line and saves to session state.
    """
    # Create map centered on Alaska
    m = folium.Map(location=[64.2008, -149.4937], zoom_start=4)

    # Enable only polyline drawing
    draw = Draw(
        draw_options={
            "polyline": {
                "shapeOptions": {
                    "color": 'blue',   
                    "weight": 4,
                    "opacity": 0.8
                }
            },
            "polygon": False,
            "circle": False,
            "rectangle": False,
            "circlemarker": False,
            "marker": False,
        },
        edit_options={"edit": True}
    )
    draw.add_to(m)

    # Add geocoder control
    add_small_geocoder(m)

    # Render map in Streamlit
    output = st_folium(m, width=700, height=500)

    # If a line was drawn, save coordinates
    if output and "all_drawings" in output and output["all_drawings"]:
        last = output["all_drawings"][-1]
        if last["geometry"]["type"] == "LineString":
            coords = last["geometry"]["coordinates"]  # list of [lon, lat]
            # ✅ Reformat to [lat, lon] pairs, rounded
            formatted = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]

            st.session_state.selected_route = formatted
            st.success(f"Loaded Route with {len(formatted)} points")
