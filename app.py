
import streamlit as st
from streamlit_folium import st_folium
from streamlit_scroll_to_top import scroll_to_here
import folium
from folium.plugins import Draw, Geocoder, Search
import geopandas as gpd
import tempfile
import zipfile

from map import add_small_geocoder
from shapefile_upload import point_shapefile, polyline_shapefile
from enter_value_upload import enter_latlng, enter_mileposts
from draw_upload import draw_point, draw_line
from details_form import project_details_form
from aashtoware import aashtoware_project, aashtoware_point
from contacts import contacts_list
from instructions import instructions
from review import review_information
from district_queries import run_district_queries


st.set_page_config(page_title="Alaska DOT&PF - APEX Project Creator", page_icon="📝", layout="centered")

# Base overview map
m = folium.Map(location=[64.2008, -149.4937], zoom_start=4)
add_small_geocoder(m)


# Initialize session state
defaults = {
    "step": 1,
    "selected_point": None,
    "selected_route": None,
    "project_type": None,
    "geo_option": None,
    "info_option": None,
    "aashto_id": "",
    "project_name": "",
    "project_description": "",
    "project_category": None,
    "project_contacts": None,
    'details_complete': False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

import streamlit as st
from streamlit_scroll_to_top import scroll_to_here

TOTAL_STEPS = 5
if "step" not in st.session_state:
    st.session_state.step = 1

# --- Initialize scroll flags ---
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False

# --- Handle scroll action ---
if st.session_state.scroll_to_top:
    scroll_to_here(0, key="top")  # 0 = instant scroll
    st.session_state.scroll_to_top = False  # reset after scrolling

# --- Navigation functions ---
def next_step():
    if st.session_state.step < TOTAL_STEPS:
        st.session_state.step += 1
    st.session_state.scroll_to_top = True  # trigger scroll

def prev_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1
    st.session_state.scroll_to_top = True  # trigger scroll



# Header and progress
st.title("📝 ADD NEW APEX PROJECT")
st.markdown("##### COMPLETE STEPS TO ADD A NEW PROJECT TO THE APEX DATABASE")
st.progress(st.session_state.step / TOTAL_STEPS)
st.caption(f"Step {st.session_state.step} of {TOTAL_STEPS}")
st.write("")

# Step content
if st.session_state.step == 1:
    st.header("Welcome")
    st.write("""
        ##### Alaska DOT&PF APEX Project Creator

        Follow these steps to create a new project in the system:

        **Step 1: Enter Project Information**  
        Provide project details either by pulling data from the AASHTOWare database or entering them manually.  
        Review and complete all required fields to ensure accuracy.

        ---

        **Step 2: Add Project Contacts**  
        Assign roles to project contacts and enter available details such as name, email, and phone.  
        Use **Add Contact** to build a list of contacts, and remove any entries if needed.  
        Confirm that all necessary contacts are included before continuing.

        ---

        **Step 3: Upload Geospatial Data**  
        Select the project type (**Site** or **Route**) and upload or create the corresponding geometry.  
        Choose the upload method that best matches your data (shapefile, coordinates, or map input).  
        Verify that the geometry is correct and reflects your project scope.

        ---

        **Step 4: Review and Confirm**  
        Check all project information, contacts, and geospatial data for completeness and accuracy.  
        Make any adjustments before finalizing.

        ---

        **Step 5: Submit Project**  
        Click **Submit** to validate the data.  
        Once approved, the project will be saved to the database and you can proceed to the next workflow stage.
        """)

    st.info("Click **Next** to begin.")

elif st.session_state.step == 2:
    st.markdown("### PROJECT INFORMATION 📄")
    st.write(
    "Choose either the AASHTOWare source or User Input to provide project details. "
    "Complete the form, then click **Submit** to save and continue."
    )

    instructions("Project Information")

    st.write("")
    st.write("")

    st.markdown("<h5>Choose Source</h5>", unsafe_allow_html=True)
    info_option = st.segmented_control(
        "Choose Source Method:",
        ["AASHTOWare Database", "User Input"],
        default=None
    )
    st.session_state.info_option = info_option

    st.write("")

    if info_option == "AASHTOWare Database":
        st.markdown("<h5>Select Project & Complete Form</h5>", unsafe_allow_html=True)
        aashtoware_project()
    elif info_option == "User Input":
        st.markdown("<h5>Complete Form</h5>", unsafe_allow_html=True)
        project_details_form(is_awp=False)

    st.write("")
    st.write("")

elif st.session_state.step == 3:
    st.markdown("### ADD CONTACTS 👥")
    st.write(
    "Complete the contact form by adding all available project contacts. "
    "Once the list is finalized, proceed to the next step."
    )

    instructions("Contacts")

    st.write("")
    st.write("")

    st.markdown("<h5>Contact Information</h5>", unsafe_allow_html=True)
    contacts_list()



elif st.session_state.step == 4:
    st.markdown("### LOAD GEOMETRY 📍")
    st.write(
        "Select the project type and provide its geometry. "
        "After choosing a type, you will see the available upload methods. "
        "Review the instructions below for detailed guidance before continuing."
    )

    instructions("Load Geometry")

    st.write("")
    st.write("")

    # --- Choose Site or Route ---
    st.markdown("<h5>Choose Project Type</h5>", unsafe_allow_html=True)
    st.session_state['project_type'] = st.segmented_control(
        "Select Project Type:",
        ["Site Project", "Route Project"],
        default=st.session_state.get('project_type', None)  # persist previous choice
    )

    # If project_type changed, clear all district values and geometry
    if st.session_state.get("prev_project_type") != st.session_state['project_type']:
        st.session_state.house_string = ""
        st.session_state.senate_string = ""
        st.session_state.borough_string = ""
        st.session_state.region_string = ""
        st.session_state.selected_point = None
        st.session_state.selected_route = None
        st.session_state['option'] = None
        st.session_state.prev_project_type = st.session_state['project_type']

    st.write("")
    if st.session_state['project_type']:
        st.markdown("<h5>Upload Geospatial Data</h5>", unsafe_allow_html=True)

        show_awp_option = (
            st.session_state.info_option == "AASHTOWare Database"
            and st.session_state['project_type'].startswith("Site")
            and st.session_state.get("awp_dcml_latitude")
            and st.session_state.get("awp_dcml_longitude")
        )

        # --- Site Project ---
        if st.session_state['project_type'].startswith("Site"):
            options = ["Upload Shapefile", "Enter Latitude/Longitude", "Select Point on Map"]
            if show_awp_option:
                options.append("AASHTOWare")

            # Ensure default is valid
            prev_option = st.session_state.get('option')
            if prev_option not in options:
                prev_option = options[0]

            st.session_state['option'] = st.segmented_control(
                "Choose Upload Method:",
                options,
                default=prev_option
            )
            option = st.session_state['option']

            if st.session_state.get("geo_option") != option:
                st.session_state.selected_point = None
                st.session_state.selected_route = None
            st.session_state.geo_option = option

            if option == "AASHTOWare":
                aashtoware_point(st.session_state.get("awp_dcml_latitude"), st.session_state.get("awp_dcml_longitude"))
                st.session_state.selected_route = None
            elif option == "Upload Shapefile":
                point_shapefile()
                st.session_state.selected_route = None
            elif option == "Select Point on Map":
                draw_point()
                st.session_state.selected_route = None
            elif option == "Enter Latitude/Longitude":
                enter_latlng()
                st.session_state.selected_route = None

        # --- Route Project ---
        else:
            options = ["Upload Shapefile", "Enter Mileposts", "Draw Route on Map"]

            # Ensure default is valid
            prev_option = st.session_state.get('option')
            if prev_option not in options:
                prev_option = options[0]

            st.session_state['option'] = st.segmented_control(
                "Choose Upload Method:",
                options,
                default=prev_option
            )
            option = st.session_state['option']

            if st.session_state.get("geo_option") != option:
                st.session_state.selected_point = None
                st.session_state.selected_route = None
            st.session_state.geo_option = option

            if option == "Upload Shapefile":
                polyline_shapefile()
                st.session_state.selected_point = None
            elif option == "Enter Mileposts":
                enter_mileposts()
                st.session_state.selected_point = None
            elif option == "Draw Route on Map":
                draw_line()
                st.session_state.selected_point = None

        # --- Track previous values ---
        if "prev_selected_point" not in st.session_state:
            st.session_state.prev_selected_point = None
        if "prev_selected_route" not in st.session_state:
            st.session_state.prev_selected_route = None

        point_val = st.session_state.get("selected_point")
        route_val = st.session_state.get("selected_route")

        point_changed = point_val is not None and point_val != st.session_state.prev_selected_point
        route_changed = route_val is not None and route_val != st.session_state.prev_selected_route

        if point_changed or route_changed:
            run_district_queries()
            st.session_state.prev_selected_point = point_val
            st.session_state.prev_selected_route = route_val

        # --- Collect values ---
        house_val = st.session_state.get('house_string')
        senate_val = st.session_state.get('senate_string')
        borough_val = st.session_state.get('borough_string')
        region_val = st.session_state.get('region_string')

        # --- Show expander if geometry has content ---
        if st.session_state['project_type'].startswith("Site") and point_val is not None and any([house_val, senate_val, borough_val, region_val]):
            with st.expander("PROJECT GEOGRAPHIES", expanded=True):
                col1, col2 = st.columns(2)
                col1.markdown(f"**House Districts:** {house_val or '—'}")
                col2.markdown(f"**Senate Districts:** {senate_val or '—'}")
                col1.markdown(f"**Boroughs:** {borough_val or '—'}")
                col2.markdown(f"**Regions:** {region_val or '—'}")

        elif st.session_state['project_type'].startswith("Route") and route_val is not None and any([house_val, senate_val, borough_val, region_val]):
            with st.expander("PROJECT GEOGRAPHIES", expanded=True):
                col1, col2 = st.columns(2)
                col1.markdown(f"**House Districts:** {house_val or '—'}")
                col2.markdown(f"**Senate Districts:** {senate_val or '—'}")
                col1.markdown(f"**Boroughs:** {borough_val or '—'}")
                col2.markdown(f"**Regions:** {region_val or '—'}")



elif st.session_state.step == 5:
    st.markdown("### REVIEW & SUBMIT ✔️")
    st.write(
    "Review all submitted project information carefully. "
    "Confirm details are correct before pressing Submit. "
    "Once submitted, the project will be loaded into the APEX Database.")

    instructions("Review")

    st.write("")
    st.write("")

    review_information()

    st.write("")

# Navigation controls with validation
st.write("")
cols = st.columns([1, 1, 4])
with cols[0]:
    st.button("⬅️ Back", on_click=prev_step, disabled=st.session_state.step == 1)

with cols[1]:
    can_proceed = False

    if st.session_state.step == 1:
        can_proceed = True
    elif st.session_state.step == 2:
        can_proceed = st.session_state.get("details_complete", False)
    elif st.session_state.step == 3:
        can_proceed = True
    elif st.session_state.step == 4:
        if st.session_state.project_type:
            if st.session_state.project_type.startswith("Site"):
                can_proceed = st.session_state.selected_point is not None
            else:
                can_proceed = st.session_state.selected_route is not None
        else:
            can_proceed = False
    elif st.session_state.step == 5:
        can_proceed = True

    if st.session_state.step < TOTAL_STEPS:
        st.button("Next ➡️", on_click=next_step, disabled=not can_proceed)


st.caption("Use Back and Next to navigate. Refresh will reset this session.")
