import streamlit as st
from streamlit_folium import st_folium
import folium
from map import set_bounds_route


def review_information():

    # --- Project Name ---
    project_name = st.session_state.get("proj_name", "")
    awp_proj_name = st.session_state.get("awp_proj_name", "—")
    display_name = project_name if project_name else awp_proj_name
    st.markdown(f"<h3>{display_name}</h3>", unsafe_allow_html=True)

    # --- Map of Location ---
    st.markdown(f"<h4>PROJECT LOCATION</h4>", unsafe_allow_html=True)
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

    # --- Project Information ---
    st.markdown(f"<h4>PROJECT INFORMATION</h4>", unsafe_allow_html=True)

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

    # Funding
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

    # Timeline
    with st.expander("Timeline", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Anticipated Start:** {st.session_state.get('anticipated_start','—')}")
        col2.markdown(f"**Anticipated End:** {st.session_state.get('anticipated_end','—')}")

    # Impacted Communities
    with st.expander("Impacted Communities", expanded=True):
        impact_comm = st.session_state.get("impact_comm", "—")
        if isinstance(impact_comm, list):
            impact_comm_display = ", ".join(str(item) for item in impact_comm) if impact_comm else "—"
        else:
            impact_comm_display = impact_comm
        st.markdown(f"**Communities:** {impact_comm_display}")

    
    # Location details (keep route-specific fields if applicable)
    with st.expander("Location", expanded=True):
        col1, col2 = st.columns(2)
        if st.session_state.get("project_type") == "Route":
            col1.markdown(f"**Route ID:** {st.session_state.get('route_id','—')}")
            col2.markdown(f"**Route Name:** {st.session_state.get('route_name','—')}")
        # Show single-value location fields if you keep them
        col1.markdown(f"**House Districts:** {st.session_state.get('house_string','—')}")
        col2.markdown(f"**Senate Districts:** {st.session_state.get('senate_string','—')}")
        col1.markdown(f"**Boroughs:** {st.session_state.get('borough_string','—')}")
        col2.markdown(f"**DOT&PF Regions:** {st.session_state.get('region_string','—')}")

    # Status & Links
    with st.expander("Status & Links", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Project Website:** {st.session_state.get('proj_web','—')}")
        col2.markdown(f"**APEX Mapper Link:** {st.session_state.get('apex_mapper_link','—')}")
        col1.markdown(f"**APEX Info Sheet:** {st.session_state.get('apex_infosheet','—')}")
        col2.markdown(f"**APEX Project Status:** {st.session_state.get('apex_proj_status','—')}")
        col1.markdown(f"**Project Status:** {st.session_state.get('proj_status','—')}")

    st.write("")
    st.write("")

    # --- Contacts ---
    st.markdown(f"<h4>CONTACTS</h4>", unsafe_allow_html=True)
    contacts = st.session_state.get("contacts", [])
    if contacts:
        if isinstance(contacts[0], dict):
            st.table(contacts)
        else:
            for contact in contacts:
                st.write(contact)
    else:
        st.write("— No contacts provided —")

    # --- Submit Button ---
    st.write("")
    st.write("")
    st.button("Submit Project")
