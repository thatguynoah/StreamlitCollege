# IMPORTING THE DATA AND DETERMINING SETTINGS
# import math
# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import statistics as stat
from GraphMaker import *

st.set_option('deprecation.showPyplotGlobalUse', False)

# MAKING GROUP AND COLLEGE CLASS
class Group():
    def __init__(self, region, state, selectivity, status, size, colleges, name):
        self.region = region
        self.state = state
        self.selectivity = selectivity
        self.status = status
        try:
            self.size = size[0:size.index(' ')][0:-1]
        except:
            self.size = size
        self.colleges = colleges
        self.name = name # better than single


# IMPORT THE DATAb
df = pd.read_csv(r"REDUCED_DATAV5.csv", index_col="INSTNM", low_memory=False)

# MAKE THE PAGE
header = st.container()
topContent = st.container()
selectInst = st.container()
selectGroup = st.container()
graphs = st.container()
footer = st.container()

with header:
    st.title("Compare College App")
    st.subheader("The Test Guy")

with topContent:
    st.header("Some brief notes and tutorial")
    st.text("1. You can select as many criteria as you want. The app will assume no selection if")
    st.text("an input is left blank.")
    st.text("2. If the region and state conflict, no results will come up. You will have to")
    st.text("resolve that conflict.")
    st.text("3. No matter what intermediate values are used for the selectivity, the filter will")
    st.text("find all colleges between the minimum and maximum values.")
    st.text("4. Don't be alarmed if graphs take a few seconds to render, there is a lot of ")
    st.text("background calculation.")

with selectInst:
    # choose specific college
    st.header("Choose Institution")
    allColleges = list(df.index)
    institution = st.selectbox("Select University", allColleges)
    addCollege = st.button("Add College")
    if addCollege:
        # update with groups
        listCollege = list()
        listCollege.append(institution)
        group = Group(region="", state="", selectivity="", status="", size="", colleges=listCollege, name=institution)
        st.session_state[f"group{len(st.session_state) + 1}"] = group

with selectGroup:
    # choose college groups
    st.header("Input your filters:")
    region = st.selectbox("Select the Region:", ("", 'U.S. Service Schools', 'New England (CT, ME, MA, NH, RI, VT)',
                                                'Mid East (DE, DC, MD, NJ, NY, PA)', 'Great Lakes (IL, IN, MI, OH, WI)',
                                                'Plains (IA, KS, MN, MO, NE, ND, SD)', 'Southeast (AL, AR, FL, GA, KY, LA, MS, NC, SC, TN, VA, WV)',
                                                'Southwest (AZ, NM, OK, TX)', 'Rocky Mountains (CO, ID, MT, UT, WY)', 'Far West (AK, CA, HI, NV, OR, WA)'))
    state = st.selectbox("Select the State:", ("", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Conneticut",
                                              "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho",
                                              "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
                                              "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
                                              "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
                                              "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                                              "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
                                              "West Virginia", "Wisconsin", "Wyoming", "American Samoa", "Federated States of Micronesia",
                                              "Guam", "Northern Mariana Islands", "Palau", "Puerto Rico", "Virgin Islands"))
    admission = st.multiselect("Select the selectivity:", ("0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%",
                                                           "60-70%", "70-80%", "80-90%", "90-100%"))
    status = st.selectbox("Select public/private", ("", "Public Institution", "Private Institution"))
    size = st.selectbox("Select Enrollment Size:", ("", "Small: < 5,000 students", "Medium: 5,001-15,000 students",
                                                    "Large: 15,001-30,000 students", 'Huge: 30,001+ students'))

    # create groups
    createGroup = st.button("Create Group")
    if createGroup:
        colleges = ChooseGroup(df, region, state, admission, status, size) # testing func
        # update with groups
        # group = Group(region, state, admission, status, list(colleges.index)) - test
        name = ""
        group = Group(region, state, admission, status, size, colleges, name)
        st.session_state[f"group{len(st.session_state)+1}"] = group
    deleteGroups = st.button("Delete All Groups and Colleges")
    if deleteGroups:
        for key in st.session_state.keys():
            del st.session_state[key]
    st.text(f"Number of groups and colleges: {len(st.session_state)}")


with graphs:
    st.header("View results")
    search = st.button("Search Colleges")
    if search:
        # create graphics and display information
        Central_Multi_Function(st.session_state, df = df)

with footer:
    st.caption("All data used was derived from the college scorecard dataset curated by the US Department of Education")
    st.caption("All analysis is performed on 4 year institutions within the US 50 states. No US territories are included in this analysis expereince.")


