
import streamlit as st
from agol_util import get_multiple_fields
import datetime


# --- Existing helpers (unchanged) ---

def session_selectbox(
    key: str,
    label: str,
    options: list,
    default_key: str = None,
    force_str: bool = False
):
    """
    Render a Streamlit selectbox that defaults to the current session_state value
    or to another session_state key passed in as default_key. If the default value
    is not in options, it will be added. Optionally convert the default value to str.
    """
    # Determine the default value
    if default_key and default_key in st.session_state:
        default_value = st.session_state[default_key]
    elif key in st.session_state:
        default_value = st.session_state[key]
    else:
        default_value = options[0] if options else ""

    # Normalize default value
    if force_str and default_value is not None:
        default_value = str(default_value)

    # Normalize options list if force_str is True
    normalized_options = [str(opt) if force_str else opt for opt in options]

    # Only add if truly missing
    if default_value not in normalized_options and default_value is not None:
        normalized_options = [default_value] + normalized_options

    # Find the index of the default value
    default_index = normalized_options.index(default_value) if default_value in normalized_options else 0

    # Render the selectbox
    st.session_state[key] = st.selectbox(label, normalized_options, index=default_index)

    return st.session_state[key]


def impacted_comms_select():
    # Source service
    comms = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/All_Alaska_Communities_Baker/FeatureServer'
    # Get list of dicts with OverallName and DCCED_CommunityId
    comms_list = get_multiple_fields(comms, 7, ['OverallName', 'DCCED_CommunityId'])
    # Build mapping from name → id
    name_to_id = {entry["OverallName"]: entry["DCCED_CommunityId"] for entry in comms_list}
    # Multiselect widget
    selected_names = st.multiselect("Select communities:", options=list(name_to_id.keys()))
    # Map back to IDs
    selected_ids = [name_to_id[name] for name in selected_names]
    # Save to session state
    st.session_state["impact_comm"] = selected_ids
    return selected_ids


# --- Unified form ---

def project_details_form(is_awp = False):
    """
    Unified project details form that supports two modes:
    - form_type="user": plain user entry form
    - form_type="aashtoware": pre-fills and slightly alters fields based on AASHTOWare keys
    """

    # Initialize session state keys (avoid KeyError later)
    session_keys = [
        "awp_proj_name", "proj_name", "public_proj_name", "iris", "stip",
        "fed_proj_num", "proj_desc", "proj_purp", "traffic_impact",
        "proj_practice", "proj_prac", "phase", "fund_type", "fund_amount",
        "tenadd", "awarded", "award_fiscal_year", "award_date", "contractor",
        "awarded_amount", "current_contract_amount", "amount_paid_to_date",
        "anticipated_start", "anticipated_end", "construction_year",
        "new_continuing", "route_id", "route_name", "impact_comm",
        "dot_pf_region", "borough_census_area", "senate_district",
        "house_district", "proj_web", "apex_mapper_link", "apex_infosheet",
        "apex_proj_status", "proj_status", "proj_impact",
        # AWP-specific potential source keys used for prefill
        "awp_name", "awp_iris_number", "awp_funding_type",
        "awp_project_practice", "awp_award_date", "awp_awardfederalfiscalyear",
        "awp_contractor", "awp_proposal_awardedamount",
        "awp_contract_currentcontractamount", "awp_contract_amountpaidtodate",
        "awp_tentative_advertising_date", "awp_project_description",
    ]
    
    # Ensure keys exist
    for k in session_keys:
        if k not in st.session_state:
            st.session_state[k] = ""

    # If not AASHTOWare mode, clear all values
    if not is_awp:
        for k in session_keys:
            st.session_state[k] = ""

    # Helpers for conditional values
    def val(key_user: str, key_awp: str = None, coerce_float: bool = False):
        if is_awp and key_awp:
            v = st.session_state.get(key_awp, "")
        else:
            v = st.session_state.get(key_user, "")
        if coerce_float:
            try:
                return float(v or 0)
            except Exception:
                return 0.0
        return v

    with st.form("project_details_form"):
        st.markdown("<h5>1. CONSTRUCTION YEAR, PROJECT NAMES, & IDS</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["construction_year"] = st.selectbox(
                "Construction Year*",
                ['', 'CY2025', 'CY2026', 'CY2027', 'CY2028', 'CY2029', 'CY2030'],
                index=0
            )
        with col2:
            st.session_state["new_continuing"] = st.selectbox(
                "New or Continuing?", ["", "New", "Continuing"], index=0
            )

        # Project Names
        if is_awp:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state["awp_proj_name"] = st.text_input(
                    "AASHTOWare Project Name",
                    value=val("awp_proj_name", "awp_name")
                )
            with c2:
                st.session_state["proj_name"] = st.text_input(
                    "Public Project Name",
                    value=st.session_state["proj_name"]
                )
        else:
            st.session_state["proj_name"] = st.text_input(
                "Public Project Name",
                value=st.session_state["proj_name"]
            )

        # Project Identifiers
        col5, col6, col7 = st.columns(3)
        with col5:
            st.session_state["iris"] = st.text_input(
                "IRIS",
                value=val("iris", "awp_iris_number")
            )
        with col6:
            st.session_state["stip"] = st.text_input("STIP", value=st.session_state["stip"])
        with col7:
            st.session_state["fed_proj_num"] = st.text_input(
                "Federal Project Number",
                value=st.session_state["fed_proj_num"]
            )

        st.write("")
        st.write("")

        st.markdown("<h5>2. FUNDING TYPE & PRACTICE</h4>", unsafe_allow_html=True)
        col13, col14 = st.columns(2)
        with col13:
            st.session_state["fund_type"] = session_selectbox(
                key="fund_type",
                label="Funding Type?",
                options=(["", "FHWA", "FAA", "STATE", "OTHER"] if not is_awp else ["", "FHWY", "FHWA", "FAA", "STATE", "OTHER"]),
                default_key=("awp_funding_type" if is_awp else None)
            )
        with col14:
            st.session_state["proj_prac"] = session_selectbox(
                key="proj_prac",
                label="Project Practice?",
                options=['', 'Highways', "Aviation", "Facilities", "Marine Highway", "Other"],
                default_key=("awp_project_practice" if is_awp else None)
            )

        st.write("")
        st.write("")

        st.markdown("<h5>3. START & END DATE</h4>", unsafe_allow_html=True)
        col10, col11 = st.columns(2)
        with col10:
            st.session_state["anticipated_start"] = st.text_input(
                "Anticipated Start Date",
                placeholder="MM-YYYY (07-2025)",
                value=st.session_state["anticipated_start"]
            )
        with col11:
            st.session_state["anticipated_end"] = st.text_input(
                "Anticipated End Date",
                placeholder="MM-YYYY (07-2025)",
                value=st.session_state["anticipated_end"]
            )

        st.write("")
        st.write("")

        st.markdown("<h5>4. AWARD INFORMATION</h4>", unsafe_allow_html=True)
        col12, col13 = st.columns(2)
        with col12:
            st.session_state["award_date"] = st.date_input(
                "Award Date",
                format="MM/DD/YYYY",
                value=val("awp_award_date") if is_awp else None
            )
        with col13:
            st.session_state["award_fiscal_year"] = session_selectbox(
                key="award_fiscal_year",
                label="Awarded Fiscal Year",
                options=["", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"],
                default_key=("awp_awardfederalfiscalyear" if is_awp else None),
                force_str=is_awp
            )

        st.session_state["contractor"] = st.text_input(
            "Awarded Contractor",
            value=val("contractor", "awp_contractor")
        )

        col15, col16, col17 = st.columns(3)
        with col15:
            st.session_state["awarded_amount"] = st.number_input(
                "Awarded Amount",
                value=val("awarded_amount", "awp_proposal_awardedamount", coerce_float=True)
            )
        with col16:
            st.session_state["current_contract_amount"] = st.number_input(
                "Current Contract Amount",
                value=val("current_contract_amount", "awp_contract_currentcontractamount", coerce_float=True)
            )
        with col17:
            st.session_state["amount_paid_to_date"] = st.number_input(
                "Amount Paid to Date",
                value=val("amount_paid_to_date", "awp_contract_amountpaidtodate", coerce_float=True)
            )


        st.session_state["tenadd"] = st.date_input(
                "Tentative Advertise Date",
                format="MM/DD/YYYY",
                value=val("awp_tentative_advertising_date") if is_awp else None
            )

        st.write("")
        st.write("")

        st.markdown("<h5>5. DESCRIPTIONS, IMPACTS, PURPOSE</h4>", unsafe_allow_html=True)
        if is_awp:
            st.session_state["awp_proj_desc"] = st.text_area(
                "AASHTOWare Description",
                height=200,
                value=st.session_state.get("awp_project_description", "")
            )
            # Keep the public description distinct from the AWP description
            st.session_state["proj_desc"] = st.text_area(
                "Public Description",
                height=200,
                value=st.session_state["proj_desc"]
            )
        else:
            st.session_state["proj_desc"] = st.text_area(
                "Description",
                height=200,
                value=st.session_state["proj_desc"]
            )
        st.session_state["proj_purp"] = st.text_area("Purpose", height=200, value=st.session_state["proj_purp"])
        st.session_state["proj_impact"] = st.text_area("Impact", height=200, value=st.session_state["proj_impact"])

        st.write("")
        st.write("")

        st.markdown("<h5>6. WEB LINKS</h4>", unsafe_allow_html=True)
        st.session_state["proj_web"] = st.text_input("Project Website", value=st.session_state["proj_web"])
        st.session_state["apex_mapper_link"] = st.text_input("APEX Mapper", value=st.session_state["apex_mapper_link"])
        st.session_state["apex_infosheet"] = st.text_input("APEX Info Sheet", value=st.session_state["apex_infosheet"])

        st.write("")
        st.write("")

        st.markdown("<h5>7. IMPACTED COMMUNITIES</h4>", unsafe_allow_html=True)
        st.session_state["impact_comm"] = impacted_comms_select()

        st.write("")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    # Validation and post-submit output
    if submit_button:
        required_fields = {
            "Construction Year": st.session_state.get("construction_year"),
            
        }

        missing_fields = [field for field, value in required_fields.items() if not value]

        if missing_fields:
            for field in missing_fields:
                st.error(f"{field} Required")
            st.session_state.details_complete = False
        
        else:
            st.success(f"Project Information Saved")
            # Mark details as complete so navigation can proceed
            st.session_state.details_complete = True
            # Optionally store a consolidated dict for later review
            st.session_state.project_details = required_fields
