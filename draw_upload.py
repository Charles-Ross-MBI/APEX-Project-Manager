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



import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

def draw_point():
    st.write("")
    """
    Display a Folium map where the user can draw a point.

    - Map centered on Alaska.
    - Only marker drawing tool enabled.
    - Captures last drawn point and saves to session state.
    - Existing/stored point renders as a RED marker.
    """

    # Create map centered on Alaska
    m = folium.Map(location=[64.0000, -152.0000], zoom_start=4)

    # ✅ If a point already exists, add a RED marker
    if st.session_state.get('selected_point'):
        lat, lon = st.session_state['selected_point']
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="blue", icon="map-marker")
        ).add_to(m)

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

    # Add geocoder control (assuming you have this helper defined elsewhere)
    add_small_geocoder(m)

    # Render map in Streamlit
    output = st_folium(m, width=700, height=500)

    # If a point was drawn, save coordinates
    if output and "all_drawings" in output and output["all_drawings"]:
        last = output["all_drawings"][-1]
        if last.get("geometry", {}).get("type") == "Point":
            coords = last["geometry"]["coordinates"]  # [lon, lat]
            lon, lat = coords[0], coords[1]
            # ✅ Store consistently as [lat, lon]
            st.session_state['selected_point'] = [round(lat, 6), round(lon, 6)]




def draw_line():
    st.write("")
    """
    Display a Folium map where the user can draw a line.

    - Map centered on Alaska.
    - Only polyline drawing tool enabled.
    - Captures last drawn line and saves to session state.
    - Line color matches Leaflet's default blue (#3388ff), same look as the blue icon.
    """

    # Use Leaflet's standard blue for vectors
    BLUE = "#3388ff"

    # Create map centered on Alaska
    m = folium.Map(location=[64.2008, -149.4937], zoom_start=4)

    # ✅ If a route already exists, add it back to the map with the same blue
    if st.session_state.get('selected_route'):
        route = st.session_state['selected_route']  # list of [lat, lon] pairs
        folium.PolyLine(
            route,
            color=BLUE,
            weight=8,
            opacity=1
        ).add_to(m)

    # Enable only polyline drawing and force the same blue color while drawing
    draw = Draw(
        draw_options={
            "polyline": {
                "shapeOptions": {
                    "color": BLUE,    # exact Leaflet blue
                    "weight": 8,
                    "opacity": 1
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
        if last.get("geometry", {}).get("type") == "LineString":
            coords = last["geometry"]["coordinates"]  # list of [lon, lat]
            # ✅ Reformat to [lat, lon] pairs, rounded
            formatted = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]
            st.session_state['selected_route'] = formatted
