import streamlit as st


TAB_INSTRUCTIONS = {
    "Load Geometry": """
##### Step 1: Select Project Type
Start by deciding whether your project is a **Site** or a **Route**.  
This choice determines how your project will be represented in the system and which upload methods are available.

- **Site Projects:** Represented by a single point on the map.  
  Examples include airports, harbors, or buildings not located on the Alaska DOT&PF road network.  
  Choose **Site** if your project is tied to a fixed location and does not involve roadways or traffic impacts.

- **Route Projects:** Represented by a line along the road network.  
  Examples include road construction, resurfacing, or maintenance projects on the Alaska DOT&PF road network.  
  Choose **Route** if your project involves roadway segments and may affect traffic flow.

---

##### Step 2: Upload Data
Once you select a project type, you will see options for uploading the corresponding geometry.  
Different upload methods are available depending on whether you chose Site or Route:

- **For Site Projects:** You may upload a shapefile, enter latitude/longitude coordinates, or select a point directly on the map.  
- **For Route Projects:** You may upload a shapefile, enter milepost ranges, or draw the route directly on the map.  

Pick the method that best matches the data you have available.

---

##### Step 3: Confirm Accuracy
After uploading, carefully review the geometry displayed on the map.  
Make sure the location or route matches your project details.  
Confirming accuracy at this stage is important because the geometry will be used in later steps for analysis and reporting.  
If something looks incorrect, adjust or re‑upload before proceeding.

---

##### Step 4: Project Geographies
Once geometry is successfully loaded into the app, the system will automatically process and query against four Alaska State geography layers:  
- **House Districts**  
- **Senate Districts**  
- **Boroughs**  
- **DOT&PF Regions**

The results will be displayed as a list under **Project Geographies**.  
Carefully review these values to ensure they are correct for your project.  
If the districts or regions look wrong, adjust your geometry and reload before proceeding.
""",

    "Project Information": """
##### Step 1: Select Data Source
Choose how you want to provide project information. You have two options:

- **AASHTOWare Database:** Select from a dropdown list of available projects connected to AASHTOWare.  
  The form will automatically populate with the information stored in the database.  
  Review the pre‑filled details and make any necessary updates.

- **User Input:** Start with a blank form and manually enter all project information.  
  This option is useful if your project is not listed in AASHTOWare or requires custom details.

---

##### Step 2: Review and Complete Information
Regardless of the data source selected, carefully review the project information.  
Fill out all fields to the best of your ability, ensuring accuracy and completeness.

---

##### Step 3: Submit and Validate
Click **Submit** once the form is complete.  
The system will check that all required fields are filled out and properly formatted.  
If approved, the **Next** option will become available, allowing you to proceed to the following step.
""",

    "Contacts": """
##### Step 1: Add Contact Details
For each project contact, first select the appropriate **role** (e.g., Project Manager, Engineer, Contractor).  
Then provide the available details such as **name, email, and phone number**.  
If some fields are not applicable, fill in what you have.

---

##### Step 2: Add to Contact List
Once the information is entered, click **Add Contact**.  
The contact will be added to a running list displayed below.  
You may also remove a contact from the list if needed.

---

##### Step 3: Review and Continue
Ensure all required contacts have been added before proceeding.  
Review the list for accuracy and completeness.  
When finished, continue to the next step in the workflow.
""",

    "Review": """
##### Step 1: Review Entered Information
Carefully review all information entered in previous steps.  
The review will display in the following order:
- **Project Name**  
- **Submitted Project Geometry**  
- **Project Geographies**  
- **Project Information**  
- **Contacts**

---

##### Step 2: Make Updates if Needed
If any value needs to be changed, backtrack to the appropriate step and update the information.  
Once updated, return to this tab to continue.

---

##### Step 3: Submit Project
If all information is complete and correct, click **Submit**.  
The application will process the submitted data and load it into the **APEX Database**.  
Completion steps will appear as they are being performed.

---

##### Step 4: Confirmation
If the data was submitted successfully, the application will notify you.  
At that point, you may close the application or restart to add a new entry.
""",

    "Other Tab Example": """
#### Instructions
Add instructions for other tabs here as needed.
"""
}



def instructions(tab_name: str):
    """
    Display instructions for a given tab inside a Streamlit expander.
    """
    content = TAB_INSTRUCTIONS.get(tab_name)
    if content:
        with st.expander("Instructions", expanded=False):
            st.markdown(content)
    else:
        st.warning(f"No instructions found for tab: {tab_name}")