"""
Streamlit functions for drawing points and lines on a Folium map.

Users can interactively draw geometries, which are then stored
in Streamlit session state and displayed with success messages.
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw, Geocoder
from map import add_small_geocoder, set_bounds_route, set_zoom




def draw_point():
    st.write("")
    """
    Display a Folium map where the user can draw a point.

    - Map centered on Alaska.
    - Only marker drawing tool enabled.
    - Captures last drawn point and saves to session state.
    - Previously saved point remains EDITABLE after rerender and matches Draw's default icon.
    """

    # Create map centered on Alaska
    m = folium.Map(location=[64.0000, -152.0000], zoom_start=4)

    # FeatureGroup that Draw will edit
    drawn_items = folium.FeatureGroup(name="drawn_items")
    m.add_child(drawn_items)

    # ✅ Add stored point with the DEFAULT Leaflet icon (no custom icon specified)
    if st.session_state.get("selected_point"):
        lat, lon = st.session_state["selected_point"]
        folium.Marker(location=[lat, lon]).add_to(drawn_items)
        m.fit_bounds([[lat, lon]])

    # Wire Draw to the FeatureGroup; enable marker + edit/remove
    draw = Draw(
        feature_group=drawn_items,
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "rectangle": False,
            "circlemarker": False,
            "marker": True,
        },
        edit_options={
            "edit": True,
            "remove": True,
        }
    )
    draw.add_to(m)

    # Add geocoder control
    add_small_geocoder(m)

    # Render map in Streamlit
    output = st_folium(m, width=700, height=500, key="point_draw_map")

    # If a point was drawn or edited, save coordinates
    if output and "all_drawings" in output and output["all_drawings"]:
        points = [f for f in output["all_drawings"] if f.get("geometry", {}).get("type") == "Point"]
        if points:
            lon, lat = points[-1]["geometry"]["coordinates"]  # [lon, lat]
            st.session_state["selected_point"] = [round(lat, 6), round(lon, 6)]










def draw_line():
    st.write("")
    """
    Display a Folium map where the user can draw a line.

    - Map centered on Alaska.
    - Only polyline drawing tool enabled.
    - Captures last drawn line and saves to session state.
    - Previously saved line remains EDITABLE after rerender and uses Draw's default style.
    """

    # Create map centered on Alaska
    m = folium.Map(location=[64.2008, -149.4937], zoom_start=4)

    # FeatureGroup that Draw will edit
    drawn_items = folium.FeatureGroup(name="drawn_items")
    m.add_child(drawn_items)

    
    if st.session_state.get("selected_route"):
        route = st.session_state["selected_route"]
        bounds = set_bounds_route(route)
        folium.PolyLine(route).add_to(drawn_items)

        # --- swap (lat, lng) -> (lng, lat) before applying fit_bounds ---
        if m and bounds and len(bounds) == 2:
            m.zoom_start = set_zoom(bounds)
            # bounds expected shape: [[lat_min, lng_min], [lat_max, lng_max]]
            swapped_bounds = [
                [bounds[0][1], bounds[0][0]],  # [lng_min, lat_min]
                [bounds[1][1], bounds[1][0]]   # [lng_max, lat_max]
            ]
            m.fit_bounds(swapped_bounds)  # no explicit style -> default Draw style


    # Wire Draw to the FeatureGroup; enable only polyline + edit/remove
    draw = Draw(
        feature_group=drawn_items,  # <-- key: pre-existing layers in this group are editable
        draw_options={
            "polyline": True,     # allow drawing lines
            "polygon": False,
            "circle": False,
            "rectangle": False,
            "circlemarker": False,
            "marker": False,
        },
        edit_options={
            "edit": True,
            "remove": True,
        }
    )
    draw.add_to(m)

    # Add geocoder control
    add_small_geocoder(m)

    # Render map in Streamlit
    output = st_folium(m, width=700, height=500, key="line_draw_map")

    # If a line was drawn, save coordinates
    if output and "all_drawings" in output and output["all_drawings"]:
        # Find the last LineString feature returned
        lines = [f for f in output["all_drawings"] if f.get("geometry", {}).get("type") == "LineString"]
        if lines:
            coords = lines[-1]["geometry"]["coordinates"]  # list of [lon, lat]
            # ✅ Reformat to [lat, lon] pairs, rounded
            formatted = [[round(lat, 6), round(lon, 6)] for lon, lat in coords]
            st.session_state["selected_route"] = formatted

