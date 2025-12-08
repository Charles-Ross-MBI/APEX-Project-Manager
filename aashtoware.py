import streamlit as st
from streamlit_folium import st_folium
import folium
from agol_util import get_multiple_fields
from agol_util import select_record
from details_form import project_details_form
from map import add_small_geocoder



def aashtoware_point(lat: float, lon: float):
    st.write("")

    # Two columns for lat and lon inputs
    cols = st.columns(2)
    with cols[0]:
        lat_val = st.number_input(
            "Latitude",
            value=float(lat),
            format="%.6f",
            key="awp_lat"
        )
    with cols[1]:
        lon_val = st.number_input(
            "Longitude",
            value=float(lon),
            format="%.6f",
            key="awp_lon"
        )

    # Create map centered on the coordinates
    m = folium.Map(location=[lat_val, lon_val], zoom_start=10)
    folium.Marker([lat_val, lon_val], popup=f"Lat: {lat_val}, Lon: {lon_val}").add_to(m)
    add_small_geocoder(m)
    st_folium(m, width=700, height=500)
    
    # ✅ Update session_state if valid point
    if lat_val and lon_val:
        try:
            st.session_state["selected_point"] = [round(float(lat_val), 6), round(float(lon_val), 6)]
        except Exception:
            st.session_state["selected_point"] = None







def aashtoware_project():
    aashtoware = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/AWP_PROJECTS_EXPORT_XYTableToPoint_ExportFeatures/FeatureServer'

    # Pull a subset of fields for the dropdown
    aashtoware_projects = get_multiple_fields(aashtoware, 0, ["Name", "ProposalId", "StateProjectNumber", "GlobalId"])
    
    # Build a mapping of display labels -> GlobalID
    options = {
        f"{p.get('StateProjectNumber', '')} – {p.get('Name', '')}": p.get("GlobalID")
        for p in aashtoware_projects
        if p.get("GlobalID")  # ensure valid ID
    }

    # Dropdown list with no default selection
    selected_label = st.selectbox(
        "AASHTOWare Project List",
        list(options.keys()),
        index=None,
        placeholder="Select Project"
    )

    # Map selection to GlobalID and save to session_state
    aashto_id = options.get(selected_label) if selected_label else None
    st.session_state["aashto_id"] = aashto_id

    # Optional feedback
    if aashto_id:
        # Pull the full record for the selected project
        record = select_record(aashtoware, 0, "GlobalID", aashto_id)
        
        if record and "attributes" in record[0]:
            attributes = record[0]["attributes"]
            
            # Cycle through each field and store in session_state
            for key, value in attributes.items():
                session_key = f"awp_{key.lower()}"
                st.session_state[session_key] = value
            
            project_details_form(is_awp=True)
    