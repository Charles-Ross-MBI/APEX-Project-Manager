
# review.py
import streamlit as st
from streamlit_folium import st_folium
import folium
from map import set_bounds_route




# Dialog for confirmation
@st.dialog("Confirm Submission")
def confirm_submit_dialog():
    st.write(
        "You're about to submit this project to the APEX database. "
        "Please confirm all information has been reviewed."
    )
    st.write("**This action cannot be undone from this workflow.**")

    # Two side-by-side buttons
    col_ok, col_cancel = st.columns(2)

    with col_ok:
        # Blue primary confirm button
        if st.button("Confirm & Submit", type="primary"):
            # TODO: call your final submission routine here
            # e.g., save_to_apex(st.session_state)
            st.session_state["submitted"] = True
            st.success("Project submitted.")
            # Optionally jump back to review or to a 'done' page
            st.session_state["step"] = 5
            st.session_state["scroll_to_top"] = True
            st.rerun()

    with col_cancel:
        # Neutral gray cancel button
        if st.button("Cancel", type="secondary"):
            # Just close the dialog
            st.session_state["show_confirm_dialog"] = False
            st.rerun()

    




# ----------------------------------------------------------------------
# Navigation helpers
# ----------------------------------------------------------------------
def goto_step(target_step: int):
    """Set the wizard step and rerun immediately."""
    st.session_state["step"] = target_step
    # Keep UX consistent with your app's scroll behavior
    st.session_state["scroll_to_top"] = True
    st.rerun()

def header_with_edit(title: str, target_step: int, *, help: str = None):
    """Render a left-aligned section header with a right-aligned EDIT button."""
    left, right = st.columns([1, 0.18])  # adjust ratios to taste
    with left:
        st.markdown(f"<h4 style='margin-bottom:0'>{title}</h4>", unsafe_allow_html=True)
    with right:
        st.button("✏️ EDIT", help=help, on_click=goto_step, args=(target_step,))


# ----------------------------------------------------------------------
# Review page
# ----------------------------------------------------------------------
def review_information():
    """
    Render the review page with section headers and a single EDIT button for Project Information.
    Buttons navigate to the correct step in the wizard:
      - Step 2: Project Information (includes Identification, Narrative, Funding, Timeline,
                Impacted Communities, Status & Links)
      - Step 3: Contacts
      - Step 4: Project Location & Location Details
      - Step 5: Review (this page)
    """

    # --- Project Name ---
    project_name = st.session_state.get("proj_name", "")
    awp_proj_name = st.session_state.get("awp_proj_name", "—")
    display_name = project_name if project_name else awp_proj_name
    st.markdown(f"<h3>{display_name}</h3>", unsafe_allow_html=True)

    # --- Map of Location ---
    header_with_edit("PROJECT LOCATION", target_step=4, help="Edit geometry & geographies")
    m = None
    if st.session_state.get("selected_point"):
        lat, lon = st.session_state.selected_point
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup="Project Point").add_to(m)
    elif st.session_state.get("selected_route"):
        route = st.session_state.selected_route  # list of [lat, lon]
        m = folium.Map(location=route[0], zoom_start=10)
        folium.PolyLine(route, color="blue", weight=3).add_to(m)
        # Convert [lat, lon] -> [lon, lat] for bounds helper
        route_bounds = [(lon, lat) for (lat, lon) in st.session_state.selected_route]
        m.fit_bounds(set_bounds_route(route_bounds))
    if m:
        st_folium(m, width=700, height=400)

    st.write("")
    st.write("")

    # --- Project Information (single EDIT button for the whole section) ---
    header_with_edit("PROJECT INFORMATION", target_step=2, help="Edit all project information")

    # Identification
    with st.expander("Identification", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Construction Year:** {st.session_state.get('construction_year','—')}")
        col2.markdown(f"**New/Continuing:** {st.session_state.get('new_continuing','—')}")
        col1.markdown(f"**Public Project Name:** {st.session_state.get('public_proj_name','—')}")
        col2.markdown(f"**IRIS:** {st.session_state.get('iris','—')}")
        col1.markdown(f"**STIP:** {st.session_state.get('stip','—')}")
        col2.markdown(f"**Federal Project Number:** {st.session_state.get('fed_proj_num','—')}")
        col1.markdown(f"**Practice:** {st.session_state.get('proj_prac','—')}")

    # Narrative (Purpose, Description, Impact)
    with st.expander("Purpose, Description & Impact", expanded=True):
        st.markdown(f"**Purpose:**\n\n{st.session_state.get('proj_purp','—')}")
        if st.session_state.get("info_option") == "AASHTOWare Database":
            st.markdown(f"**AASHTOWare Description:**\n\n{st.session_state.get('awp_proj_desc','—')}")
            st.markdown(f"**Public Project Description:**\n\n{st.session_state.get('proj_desc','—')}")
        else:
            st.markdown(f"**Project Description:**\n\n{st.session_state.get('proj_desc','—')}")
        st.markdown(f"**Impact:**\n\n{st.session_state.get('proj_impact','—')}")

    # Funding (no separate EDIT button)
    with st.expander("Funding", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Fund Type:** {st.session_state.get('fund_type','—')}")
        col2.markdown(f"**Fund Amount:** {st.session_state.get('fund_amount','—')}")
        col1.markdown(f"**Awarded:** {st.session_state.get('awarded','—')}")
        col2.markdown(f"**Award Fiscal Year:** {st.session_state.get('award_fiscal_year','—')}")
        col1.markdown(f"**Award Date:** {st.session_state.get('award_date','—')}")
        col2.markdown(f"**Contractor:** {st.session_state.get('contractor','—')}")
        col1.markdown(
            "**Awarded Amount:** "
            + (("${:,.0f}".format(float(st.session_state.get("awarded_amount", 0))))
               if st.session_state.get("awarded_amount") not in (None, "") else "")
        )
        col2.markdown(
            "**Current Contract Amount:** "
            + (("${:,.0f}".format(float(st.session_state.get("current_contract_amount", 0))))
               if st.session_state.get("current_contract_amount") not in (None, "") else "")
        )
        col1.markdown(
            "**Amount Paid to Date:** "
            + (("${:,.0f}".format(float(st.session_state.get("amount_paid_to_date", 0))))
               if st.session_state.get("amount_paid_to_date") not in (None, "") else "")
        )
        col2.markdown(f"**Tenadd:** {st.session_state.get('tenadd','—')}")

    # Timeline (no separate EDIT button)
    with st.expander("Timeline", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Anticipated Start:** {st.session_state.get('anticipated_start','—')}")
        col2.markdown(f"**Anticipated End:** {st.session_state.get('anticipated_end','—')}")

    # Impacted Communities (no separate EDIT button)
    with st.expander("Impacted Communities", expanded=True):
        impact_comm = st.session_state.get("impact_comm_names", "—")
        if isinstance(impact_comm, list):
            impact_comm_display = ", ".join(str(item) for item in impact_comm) if impact_comm else "—"
        else:
            impact_comm_display = impact_comm
        st.markdown(f"**Communities:** {impact_comm_display}")

    # Status & Links (no separate EDIT button)
    with st.expander("Status & Links", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Project Website:** {st.session_state.get('proj_web','—')}")
        col2.markdown(f"**APEX Mapper Link:** {st.session_state.get('apex_mapper_link','—')}")
        col1.markdown(f"**APEX Info Sheet:** {st.session_state.get('apex_infosheet','—')}")
        col2.markdown(f"**APEX Project Status:** {st.session_state.get('apex_proj_status','—')}")
        col1.markdown(f"**Project Status:** {st.session_state.get('proj_status','—')}")

    st.write("")
    st.write("")

    # --- Contacts (separate page -> keep EDIT) ---
    header_with_edit("CONTACTS", target_step=3, help="Edit project contacts")
    contacts = st.session_state.get("contacts", [])
    if contacts:
        if isinstance(contacts[0], dict):
            st.table(contacts)
        else:
            for contact in contacts:
                st.write(contact)
    else:
        st.write("— No contacts provided —")

    

    # --- Submit button that opens the modal ---
    st.write("")
    st.write("")

    if st.button("SUBMIT PROJECT", type="primary"):
        st.session_state["show_confirm_dialog"] = True
        confirm_submit_dialog()


