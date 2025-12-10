import streamlit as st
import datetime
from agol_util import get_multiple_fields
from aashtoware import aashtoware_project


# --- Helpers ---

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
    Uses versioned widget keys to allow hard resets on source/project switches.
    """
    version = st.session_state.get("form_version", 0)

    if default_key and default_key in st.session_state:
        default_value = st.session_state[default_key]
    elif key in st.session_state:
        default_value = st.session_state[key]
    else:
        default_value = options[0] if options else ""

    if force_str and default_value is not None:
        default_value = str(default_value)

    normalized_options = [str(opt) if force_str else opt for opt in options]

    if default_value not in normalized_options and default_value is not None:
        normalized_options = [default_value] + normalized_options

    default_index = normalized_options.index(default_value) if default_value in normalized_options else 0

    st.session_state[key] = st.selectbox(
        label,
        normalized_options,
        index=default_index,
        key=f"{key}_{version}"
    )
    return st.session_state[key]



def impacted_comms_select():
    """
    Multiselect for impacted communities.
    - Displays community names but stores *both* IDs and names in session_state.
    - Restores selection by mapping stored IDs -> names and falling back to stored names.
    - Uses versioned widget key yet provides an explicit default to persist across versions.
    """
    version = st.session_state.get("form_version", 0)

    # Data source
    comms_url = (
        "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/"
        "All_Alaska_Communities_Baker/FeatureServer"
    )
    # Expected shape: [{"OverallName": "...", "DCCED_CommunityId": "..."}]
    comms_list = get_multiple_fields(comms_url, 7, ["OverallName", "DCCED_CommunityId"]) or []

    # Mappings
    name_to_id = {
        c["OverallName"]: c["DCCED_CommunityId"]
        for c in comms_list
        if c.get("OverallName") and c.get("DCCED_CommunityId")
    }
    id_to_name = {v: k for k, v in name_to_id.items()}

    # --- Restore previous selections across reruns/version changes ---
    prev_ids = st.session_state.get("impact_comm_ids", []) or []
    prev_names = st.session_state.get("impact_comm_names", []) or []

    # Prefer IDs -> names (IDs are canonical). If an ID no longer exists, fall back to any stored name.
    default_names_from_ids = [id_to_name[i] for i in prev_ids if i in id_to_name]
    default_names_fallback = [n for n in prev_names if n in name_to_id]  # only valid names
    default_names = default_names_from_ids or default_names_fallback

    # Render widget with explicit default so selections persist even when form_version changes
    selected_names = st.multiselect(
        "Select communities:",
        options=sorted(name_to_id.keys()),
        default=sorted(default_names),
        key=f"impact_comm_{version}",
        help="Choose one or more communities impacted by the project."
    )

    # Convert names -> IDs for storage
    selected_ids = [name_to_id[n] for n in selected_names if n in name_to_id]

    # Store both in session_state for later use
    st.session_state["impact_comm_ids"] = selected_ids
    st.session_state["impact_comm_names"] = selected_names

    # For backward compatibility with your current code path, keep this key too
    st.session_state["impact_comm"] = selected_ids

    return selected_ids



# --- Main form wrapper ---
def project_details_form():
    """
    Source selection (AASHTOWare vs User Input) using segmented_control where
    None is a valid unselected state. Forms render only when a selection is made.
    Resets/bump happen exactly when switching between the two sources.
    """

    # Initialize version counter once
    if "form_version" not in st.session_state:
        st.session_state["form_version"] = 0
    if "prev_info_option" not in st.session_state:
        st.session_state["prev_info_option"] = None

    OPTIONS = ["AASHTOWare Database", "User Input"]

    # --- Change handler: run only when selection is a non-None change ---
    def _on_source_change():
        current = st.session_state.get("info_option")  # may be None
        prev = st.session_state.get("prev_info_option")

        # If the user cleared selection (None), do nothing; no form should render.
        if current is None:
            return

        # Only react when the actual option changed (prev -> current)
        if current != prev:
            if current == "User Input":
                # Clear user-entered fields (keep impacted communities unless you want a hard reset)
                user_keys = [
                    "construction_year", "new_continuing", "proj_name", "iris", "stip",
                    "fed_proj_num", "fund_type", "proj_prac", "anticipated_start",
                    "anticipated_end", "award_date", "award_fiscal_year", "contractor",
                    "awarded_amount", "current_contract_amount", "amount_paid_to_date",
                    "tenadd", "proj_desc", "proj_purp", "proj_impact", "proj_web",
                    "apex_mapper_link", "apex_infosheet"
                    # "impact_comm", "impact_comm_ids", "impact_comm_names"  # uncomment to hard reset
                ]
                for k in user_keys:
                    st.session_state[k] = "" if k not in ["award_date", "tenadd"] else None

                # Clear AWP-specific keys and selection memory
                for k in list(st.session_state.keys()):
                    if k.startswith("awp_"):
                        st.session_state[k] = ""
                st.session_state["aashto_id"] = ""
                st.session_state["aashto_label"] = ""
                st.session_state["aashto_selected_project"] = ""

            elif current == "AASHTOWare Database":
                # Clear only user-entered fields; AWP will prefill
                user_keys = [
                    "construction_year", "new_continuing", "proj_name", "iris", "stip",
                    "fed_proj_num", "fund_type", "proj_prac", "anticipated_start",
                    "anticipated_end", "award_date", "award_fiscal_year", "contractor",
                    "awarded_amount", "current_contract_amount", "amount_paid_to_date",
                    "tenadd", "proj_desc", "proj_purp", "proj_impact", "proj_web",
                    "apex_mapper_link", "apex_infosheet"
                    # "impact_comm", "impact_comm_ids", "impact_comm_names"  # uncomment to hard reset
                ]
                for k in user_keys:
                    st.session_state[k] = "" if k not in ["award_date", "tenadd"] else None

            # Persist selection and force widget reset on re-render
            st.session_state["prev_info_option"] = current
            st.session_state["details_complete"] = False
            st.session_state["form_version"] = st.session_state.get("form_version", 0) + 1

    # --- Segmented control (None is allowed) ---
    st.segmented_control(
        "Choose Source Method:",
        OPTIONS,
        default=None,              # None is valid; nothing renders until the user selects
        key="info_option",
        on_change=_on_source_change
    )

    st.write("")  # spacer

    # --- Render only when a selection is made ---
    current_option = st.session_state.get("info_option")
    if current_option == "AASHTOWare Database":
        st.markdown("<h5>Select Project & Complete Form</h5>", unsafe_allow_html=True)
        # When an AWP project changes in aashtoware_project(), make sure it bumps form_version.
        aashtoware_project()
        _render_original_form(is_awp=True)

    elif current_option == "User Input":
        st.markdown("<h5>Complete Form</h5>", unsafe_allow_html=True)
        _render_original_form(is_awp=False)





# --- Original form renderer with versioned keys ---

def _render_original_form(is_awp: bool):
    version = st.session_state.get("form_version", 0)
    form_key = f"project_details_form_{version}"

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

    with st.form(form_key):
        st.markdown("<h5>1. CONSTRUCTION YEAR, PROJECT NAMES, & IDS</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            cy_options = ['', 'CY2025', 'CY2026', 'CY2027', 'CY2028', 'CY2029', 'CY2030']
            st.session_state["construction_year"] = st.selectbox(
                "Construction Year*",
                cy_options,
                index=(cy_options.index(st.session_state["construction_year"])
                       if st.session_state["construction_year"] in cy_options else 0),
                key=f"construction_year_{version}"
            )
        with col2:
            nc_options = ["", "New", "Continuing"]
            st.session_state["new_continuing"] = st.selectbox(
                "New or Continuing?", nc_options,
                index=(nc_options.index(st.session_state["new_continuing"])
                       if st.session_state["new_continuing"] in nc_options else 0),
                key=f"new_continuing_{version}"
            )

        # Project Names
        if is_awp:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state["awp_proj_name"] = st.text_input(
                    "AASHTOWare Project Name",
                    value=val("awp_proj_name", "awp_name"),
                    key=f"awp_proj_name_{version}"
                )
            with c2:
                st.session_state["proj_name"] = st.text_input(
                    "Public Project Name",
                    value=st.session_state["proj_name"],
                    key=f"proj_name_{version}"
                )
        else:
            st.session_state["proj_name"] = st.text_input(
                "Public Project Name",
                value=st.session_state["proj_name"],
                key=f"proj_name_{version}"
            )

        # Project Identifiers
        col5, col6, col7 = st.columns(3)
        with col5:
            st.session_state["iris"] = st.text_input(
                "IRIS",
                value=val("iris", "awp_iris_number"),
                key=f"iris_{version}"
            )
        with col6:
            st.session_state["stip"] = st.text_input(
                "STIP",
                value=st.session_state["stip"],
                key=f"stip_{version}"
            )
        with col7:
            st.session_state["fed_proj_num"] = st.text_input(
                "Federal Project Number",
                value=st.session_state["fed_proj_num"],
                key=f"fed_proj_num_{version}"
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
                value=st.session_state["anticipated_start"],
                key=f"anticipated_start_{version}"
            )
        with col11:
            st.session_state["anticipated_end"] = st.text_input(
                "Anticipated End Date",
                placeholder="MM-YYYY (07-2025)",
                value=st.session_state["anticipated_end"],
                key=f"anticipated_end_{version}"
            )

        st.write("")
        st.write("")

        st.markdown("<h5>4. AWARD INFORMATION</h4>", unsafe_allow_html=True)
        col12, col13 = st.columns(2)
        with col12:
            # Stored date if present, else AWP prefill, else None
            stored_award_date = st.session_state.get("award_date", None)
            default_award_date = stored_award_date if isinstance(stored_award_date, datetime.date) else None
            if is_awp and default_award_date is None:
                awp_date = st.session_state.get("awp_award_date", None)
                default_award_date = awp_date if isinstance(awp_date, datetime.date) else None
            st.session_state["award_date"] = st.date_input(
                "Award Date",
                format="MM/DD/YYYY",
                value=default_award_date,
                key=f"award_date_{version}"
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
            value=val("contractor", "awp_contractor"),
            key=f"contractor_{version}"
        )

        col15, col16, col17 = st.columns(3)
        with col15:
            st.session_state["awarded_amount"] = st.number_input(
                "Awarded Amount",
                value=val("awarded_amount", "awp_proposal_awardedamount", coerce_float=True),
                key=f"awarded_amount_{version}"
            )
        with col16:
            st.session_state["current_contract_amount"] = st.number_input(
                "Current Contract Amount",
                value=val("current_contract_amount", "awp_contract_currentcontractamount", coerce_float=True),
                key=f"current_contract_amount_{version}"
            )
        with col17:
            st.session_state["amount_paid_to_date"] = st.number_input(
                "Amount Paid to Date",
                value=val("amount_paid_to_date", "awp_contract_amountpaidtodate", coerce_float=True),
                key=f"amount_paid_to_date_{version}"
            )

        # Tentative Advertise Date
        stored_tenadd = st.session_state.get("tenadd", None)
        default_tenadd = stored_tenadd if isinstance(stored_tenadd, datetime.date) else None
        if is_awp and default_tenadd is None:
            awp_tenadd = st.session_state.get("awp_tentative_advertising_date", None)
            default_tenadd = awp_tenadd if isinstance(awp_tenadd, datetime.date) else None
        st.session_state["tenadd"] = st.date_input(
            "Tentative Advertise Date",
            format="MM/DD/YYYY",
            value=default_tenadd,
            key=f"tenadd_{version}"
        )

        st.write("")
        st.write("")

        st.markdown("<h5>5. DESCRIPTIONS, IMPACTS, PURPOSE</h4>", unsafe_allow_html=True)
        if is_awp:
            st.session_state["awp_proj_desc"] = st.text_area(
                "AASHTOWare Description",
                height=200,
                value=st.session_state.get("awp_project_description", ""),
                key=f"awp_proj_desc_{version}"
            )
            # Keep the public description distinct from the AWP description
            st.session_state["proj_desc"] = st.text_area(
                "Public Description",
                height=200,
                value=st.session_state["proj_desc"],
                key=f"proj_desc_{version}"
            )
        else:
            st.session_state["proj_desc"] = st.text_area(
                "Description",
                height=200,
                value=st.session_state["proj_desc"],
                key=f"proj_desc_{version}"
            )
        st.session_state["proj_purp"] = st.text_area(
            "Purpose",
            height=200,
            value=st.session_state["proj_purp"],
            key=f"proj_purp_{version}"
        )
        st.session_state["proj_impact"] = st.text_area(
            "Impact",
            height=200,
            value=st.session_state["proj_impact"],
            key=f"proj_impact_{version}"
        )

        st.write("")
        st.write("")

        st.markdown("<h5>6. WEB LINKS</h4>", unsafe_allow_html=True)
        st.session_state["proj_web"] = st.text_input(
            "Project Website",
            value=st.session_state["proj_web"],
            key=f"proj_web_{version}"
        )
        st.session_state["apex_mapper_link"] = st.text_input(
            "APEX Mapper",
            value=st.session_state["apex_mapper_link"],
            key=f"apex_mapper_link_{version}"
        )
        st.session_state["apex_infosheet"] = st.text_input(
            "APEX Info Sheet",
            value=st.session_state["apex_infosheet"],
            key=f"apex_infosheet_{version}"
        )

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
            st.session_state["details_complete"] = False
        else:
            st.success("Project Information Saved")
            st.session_state["details_complete"] = True
            st.session_state["project_details"] = required_fields

            # If in AASHTOWare mode, preserve the selected project label so the list repopulates on return
            if is_awp:
                st.session_state["aashto_selected_project"] = st.session_state.get("aashto_label", "")
