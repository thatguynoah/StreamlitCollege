# imports
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import statistics as stat
import math
import streamlit as st

# function for determining if number is float
def stringisfloat(j):
    try:
        float(j)
        return True
    except:
        return False

# determining group (for efficiency testing)
def ChooseGroup(df, region, state, admission, status, size, institution = ""):
    colleges = df
    if region != "":
        regionNames = ['U.S. Service Schools', 'New England (CT, ME, MA, NH, RI, VT)',
                       'Mid East (DE, DC, MD, NJ, NY, PA)', 'Great Lakes (IL, IN, MI, OH, WI)',
                       'Plains (IA, KS, MN, MO, NE, ND, SD)',
                       'Southeast (AL, AR, FL, GA, KY, LA, MS, NC, SC, TN, VA, WV)',
                       'Southwest (AZ, NM, OK, TX)', 'Rocky Mountains (CO, ID, MT, UT, WY)',
                       'Far West (AK, CA, HI, NV, OR, WA)']
        regionNumbers = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        regionDict = {regionNames[i]: regionNumbers[i] for i in range(len(regionNames))}
        regionNumber = regionDict[region]
        colleges = colleges.loc[colleges["REGION"] == int(regionNumber)]
    if state != "":
        stateNames = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Conneticut",
                      "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho",
                      "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
                      "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
                      "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
                      "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                      "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
                      "Washington",
                      "West Virginia", "Wisconsin", "Wyoming"]
        stateNumbers = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                        30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55,
                        56]
        stateDict = {stateNames[i]: stateNumbers[i] for i in range(len(stateNames))}
        stateNumber = stateDict[state]
        colleges = colleges.loc[colleges["ST_FIPS"] == int(stateNumber)]
    if admission != []:
        min = float(admission[0][0])
        max = float(admission[len(admission) - 1][-3])
        colleges = colleges.loc[colleges['ADM_RATE'].between(min / 10, max / 10)]
    if status != "":
        if status == "Public Institution":
            colleges = colleges.loc[colleges["CONTROL"] == 1]
        else:
            colleges = colleges.loc[colleges["CONTROL"].isin([2, 3])]
    if size != "":
        if size[0] == 'S':
            colleges = colleges.loc[colleges["UGDS"] <= 5000]
        elif size[0] == 'M':
            colleges = colleges.loc[colleges["UGDS"].between(5001, 15000)]
        elif size[0] == 'L':
            colleges = colleges.loc[colleges["UGDS"].between(15001, 30_000)]
        else:
            colleges = colleges.loc[colleges["UGDS"] >= 30_001]

    return list(colleges.index)

#  GRAPH FUNCTIONS
# central main func
def Central_Multi_Function(state, df):
    # determine labels
    labels = {}
    userLabels = []
    for group in state.keys(): # work on this some more
        try:
            regionName = state[group].region[0:state[group].region.index('(')]
        except:
            pass
        selectivityLabel = ''
        try:
            selectivityLabel = f"{int(state[group].selectivity[0][0])*10}-{int(state[group].selectivity[-1][-3])*10}"
        except:
            pass

        if state[group].name != "": # create single college label here
            groupLabel = f"{state[group].name}"
        else:
            groupLabel = f"{f'{state[group].size} sized ' if state[group].size != '' else ''}{f'{state[group].status}s ' if state[group].status != '' else 'Colleges '}{f'in {state[group].state}' if state[group].state != '' else ''}{f'in the {regionName[0:-1]}' if state[group].state == '' and state[group].region != '' else ''}{f' with {selectivityLabel}% acceptance' if state[group].selectivity != [] else ''}"
        label = ''
        counter = 0
        for x in range(len(groupLabel)):
            label += groupLabel[x]
            counter += 1
            if counter > 20 and x != 0 and groupLabel[x] == ' ':
                label += '\n'
                counter = 0
        labels[group] = label
        userLabels.append(groupLabel)

    # call lower level graphic functions
    # average net prince per income level summary
    try:
        cost_per_income_level_comp(state, df, labels, userLabels) # HERE with single college data
    except:
        pass
    # debt accumulation for different income cohorts
    try:
        debt_per_income(state, df, labels) # df is changed to data in the function (orignially)
    except:
        pass
    # loan debt at different percentiles
    try:
        loan_debt_comparison(state, df, labels) # df is changed initially to data in the function
    except:
        pass
    # compare income after 6 years of entry and in the job market
    try:
        compare_earnings_6(state, df, labels) # df is changed initially to data in the function
    except:
        pass
    # compare income after 8 years of entry and in the job market
    try:
        compare_earnings_8(state, df, labels) # df is changed initially to data in the function
    except:
        pass
    # comapre income after 10 years of entry and in the job market
    try:
        compare_earnings_10(state, df, labels) # df is changed initially to data in the function
    except:
        pass
    # compare the popularity of different degrees
    try:
        compare_degree_popularity(state, df, labels) # df is changed initially to data in the function
    except:
        pass
    # compare the ACT scores
    # will deal with error handling inside the function
    compare_ACT(state, df, labels) # df changed initially to data at beginning of function
    # compare the SAT Scores
    try:
        compare_SAT(state, df, labels) # df changed initially to data at beginning of the function
    except:
        pass


# comparing the cost at each interval
def cost_per_income_level_comp(state, data, labels, userLabels):
    # iterate through institutions and create list of vars
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :]
        publicNames = list(df.loc[df["CONTROL"] == 1].index)
        privNames = list(df.loc[df["CONTROL"].isin([2, 3])].index)


        # NPT41
        try:
            NPT41Pub = list(df.loc[publicNames, "NPT41_PUB"])
            NPT41Priv = list(df.loc[privNames, "NPT41_PRIV"])
            NPT41Tot = NPT41Pub + NPT41Priv
            NPT41 = stat.mean([item for item in NPT41Tot if not(math.isnan(item)) == True])
        except:
            NPT41 = 0

        # NPT42
        try:
            NPT42Pub = list(df.loc[publicNames, "NPT42_PUB"])
            NPT42Priv = list(df.loc[privNames, "NPT42_PRIV"])
            NPT42Tot = NPT42Pub + NPT42Priv
            NPT42 = stat.mean([item for item in NPT42Tot if not (math.isnan(item)) == True])
        except:
            NPT42 = 0

        # NPT43
        try:
            NPT43Pub = list(df.loc[publicNames, "NPT43_PUB"])
            NPT43Priv = list(df.loc[privNames, "NPT43_PRIV"])
            NPT43Tot = NPT43Pub + NPT43Priv
            NPT43 = stat.mean([item for item in NPT43Tot if not (math.isnan(item)) == True])
        except:
            NPT43 = 0

        # NPT44
        try:
            NPT44Pub = list(df.loc[publicNames, "NPT44_PUB"])
            NPT44Priv = list(df.loc[privNames, "NPT44_PRIV"])
            NPT44Tot = NPT44Pub + NPT44Priv
            NPT44 = stat.mean([item for item in NPT44Tot if not (math.isnan(item)) == True])
        except:
            NPT44 = 0

        # NPT45
        try:
            NPT45Pub = list(df.loc[publicNames, "NPT45_PUB"])
            NPT45Priv = list(df.loc[privNames, "NPT45_PRIV"])
            NPT45Tot = NPT45Pub + NPT45Priv
            NPT45 = stat.mean([item for item in NPT45Tot if not (math.isnan(item)) == True])
        except:
            NPT45 = 0

        graphVars.append([NPT41, NPT42, NPT43, NPT44, NPT45])
        graphDict[labels[group]] = graphVars[-1]

    # plot data
    ticks = ["0-30K", "30-48K", "48-75K", "75-100K", "100K+"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="bar", rot=0)
    plt.title("Net Price Per Income Level Comparison", fontsize=16)
    plt.xlabel("Cohort Income", fontsize=14)
    plt.ylabel("Cost", fontsize=14)

    ax.legend(bbox_to_anchor=(1, 1), handlelength = 1)

    st.pyplot(ax.plot())

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="net_price_comparison.csv")

# comparing the debt at each income level
def debt_per_income(state, data, labels): # still need work (try far west private vs. far west public) !!!
    # collect data
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :] # narrow dataset once
        med_debt, low_inc_debt, md_inc_debt, hi_inc_debt = 0, 0, 0, 0 # initialize to avoid errors
        try:
            tempList = list(df.loc[:, "DEP_DEBT_MDN"]) # assume dependent students
            tempList = [i for i in tempList if type(i) != float] # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)] # removed suppressed values
            med_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "LO_INC_DEBT_MDN"])
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            low_inc_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "MD_INC_DEBT_MDN"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            md_inc_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "HI_INC_DEBT_MDN"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            hi_inc_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass

        graphVars.append([med_debt, low_inc_debt, md_inc_debt, hi_inc_debt])
        graphDict[labels[group]] = graphVars[-1]

    # plot the data
    ticks = ["Median", "0-30K", "30-75K", "75K+"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="bar", rot=0)
    plt.xlabel("Family Income Level", fontsize=14)
    plt.ylabel("Average Debt", fontsize=14)
    plt.title("Income Level vs. Average Debt Comparison", fontsize=16)
    ax.legend(bbox_to_anchor=(1, 1))

    st.pyplot(ax.plot())

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="debt_burden_comparison.csv")

# loan debt percentile comparison
def loan_debt_comparison(state, data, labels):
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :] # narrow dataset once
        debt_90, debt_75, debt_25, debt_10 = 0, 0, 0, 0 # initialize to avoid errors
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P90"]) # assume dependent students
            tempList = [i for i in tempList if type(i) != float] # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)] # removed suppressed values
            debt_90 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P75"])
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            debt_75 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P25"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            debt_25 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P10"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            debt_10 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass

        graphVars.append([debt_10, debt_25, debt_75, debt_90])
        graphDict[labels[group]] = graphVars[-1]

    ticks = ["10th", "25th", "75th", "90th"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="barh", rot=0)
    plt.xlabel("Debt", fontsize=14)
    plt.ylabel("Percentile", fontsize=14)
    plt.title("Loan Debt at Population Percentiles", fontsize=16)
    ax.legend(bbox_to_anchor=(1, 1))

    st.pyplot(ax.plot())

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="loan_debt_comparison.csv")

# compare earnings after 6 years of entry
def compare_earnings_6(state, data, labels):
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :]  # narrow dataset once
        earn_90, earn_75, earn_25, earn_10, earn_50 = 0, 0, 0, 0, 0  # initialize to avoid errors
        try: # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT90_EARN_WNE_P6"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]  # removed suppressed values
            earn_90 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT75_EARN_WNE_P6"])
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_75 = stat.mean([item for item in tempList])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT25_EARN_WNE_P6"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_25 = stat.mean([item for item in tempList])
        except:
            pass
        try: # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT10_EARN_WNE_P6"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            earn_10 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "MD_EARN_WNE_P6"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_50 = stat.mean([item for item in tempList])
        except:
            pass

        graphVars.append([earn_10, earn_25, earn_50, earn_75, earn_90])
        graphDict[labels[group]] = graphVars[-1]

    ticks = ["10th", "25th", "50th", "75th", "90th"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="barh", rot=0)
    plt.xlabel("Earnings", fontsize=14)
    plt.ylabel("Percentile", fontsize=14)
    plt.title("Income 6 Years After Entry", fontsize=16)
    ax.legend(bbox_to_anchor=(1, 1))

    st.pyplot(ax.plot())

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="six_year_earnings_comparison.csv")


# compare earnings after 8 years of entry
def compare_earnings_8(state, data, labels):
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :]  # narrow dataset once
        earn_90, earn_75, earn_25, earn_10, earn_50 = 0, 0, 0, 0, 0  # initialize to avoid errors
        try:  # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT90_EARN_WNE_P8"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]  # removed suppressed values
            earn_90 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT75_EARN_WNE_P8"])
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_75 = stat.mean([item for item in tempList])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT25_EARN_WNE_P8"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_25 = stat.mean([item for item in tempList])
        except:
            pass
        try:  # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT10_EARN_WNE_P8"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            earn_10 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "MD_EARN_WNE_P8"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_50 = stat.mean([item for item in tempList])
        except:
            pass

        graphVars.append([earn_10, earn_25, earn_50, earn_75, earn_90])
        graphDict[labels[group]] = graphVars[-1]

    ticks = ["10th", "25th", "50th", "75th", "90th"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="barh", rot=0)
    plt.xlabel("Earnings", fontsize=14)
    plt.ylabel("Percentile", fontsize=14)
    plt.title("Income 8 Years After Entry", fontsize=16)
    ax.legend(bbox_to_anchor=(1, 1))

    st.pyplot(ax.plot())

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="eight_year_earnings_comparison.csv")

# compare earnings after 10 years of entry
def compare_earnings_10(state, data, labels):
    graphVars = []
    graphDict = {}

    for group in state:
        df = data.loc[state[group].colleges, :]  # narrow dataset once
        earn_90, earn_75, earn_25, earn_10, earn_50 = 0, 0, 0, 0, 0  # initialize to avoid errors
        try:  # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT90_EARN_WNE_P10"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]  # removed suppressed values
            earn_90 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT75_EARN_WNE_P10"])
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_75 = stat.mean([item for item in tempList])
        except:
            pass
        try:
            tempList = list(df.loc[:, "PCT25_EARN_WNE_P10"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_25 = stat.mean([item for item in tempList])
        except:
            pass
        try:  # basically, this var reads as a string (so that's weird)
            tempList = list(df.loc[:, "PCT10_EARN_WNE_P10"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric() or stringisfloat(i)]
            earn_10 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "MD_EARN_WNE_P10"])  # assume dependent students
            tempList = [i for i in tempList if not (math.isnan(i)) == True]  # remove nans
            tempList = [float(i) for i in tempList]
            earn_50 = stat.mean([item for item in tempList])
        except:
            pass

        graphVars.append([earn_10, earn_25, earn_50, earn_75, earn_90])
        graphDict[labels[group]] = graphVars[-1]

    ticks = ["10th", "25th", "50th", "75th", "90th"]

    MultiBar_df = pd.DataFrame(graphDict, index=ticks)

    ax = MultiBar_df.plot(kind="barh", rot=0)
    plt.xlabel("Earnings", fontsize=14)
    plt.ylabel("Percentile", fontsize=14)
    plt.title("Income 10 Years After Entry", fontsize=16)
    ax.legend(bbox_to_anchor=(1, 1))

    st.pyplot(ax.plot())

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        tempName = group.replace("\n", "")
        st.text(f"{tempName}: {roundNumb}")

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=MultiBar_df.to_csv(), file_name="ten_year_earnings_comparison.csv")

# make graph displaying the top 5 majors of each school
def compare_degree_popularity(state, data, labels): # start debugging to just show raw data, no styling yet
    # make dictionary of category names and the values of each of the degrees
    categoryVars = ['Percentage of degrees awarded in Agriculture, Agriculture Operations, And Related Sciences.',
                     'Percentage of degrees awarded in Natural Resources And Conservation.',
                     'Percentage of degrees awarded in Architecture And Related Services.',
                     'Percentage of degrees awarded in Area, Ethnic, Cultural, Gender, And Group Studies.',
                     'Percentage of degrees awarded in Communication, Journalism, And Related Programs.',
                     'Percentage of degrees awarded in Communications Technologies/Technicians And Support Services.',
                     'Percentage of degrees awarded in Computer And Information Sciences And Support Services.',
                     'Percentage of degrees awarded in Personal And Culinary Services.',
                     'Percentage of degrees awarded in Education.',
                     'Percentage of degrees awarded in Engineering.',
                     'Percentage of degrees awarded in Engineering Technologies And Engineering-Related Fields.',
                     'Percentage of degrees awarded in Foreign Languages, Literatures, And Linguistics.',
                     'Percentage of degrees awarded in Family And Consumer Sciences/Human Sciences.',
                     'Percentage of degrees awarded in Legal Professions And Studies.',
                     'Percentage of degrees awarded in English Language And Literature/Letters.',
                     'Percentage of degrees awarded in Liberal Arts And Sciences, General Studies And Humanities.',
                     'Percentage of degrees awarded in Library Science.',
                     'Percentage of degrees awarded in Biological And Biomedical Sciences.',
                     'Percentage of degrees awarded in Mathematics And Statistics.',
                     'Percentage of degrees awarded in Military Technologies And Applied Sciences.',
                     'Percentage of degrees awarded in Multi/Interdisciplinary Studies.',
                     'Percentage of degrees awarded in Parks, Recreation, Leisure, And Fitness Studies.',
                     'Percentage of degrees awarded in Philosophy And Religious Studies.',
                     'Percentage of degrees awarded in Theology And Religious Vocations.',
                     'Percentage of degrees awarded in Physical Sciences.',
                     'Percentage of degrees awarded in Science Technologies/Technicians.',
                     'Percentage of degrees awarded in Psychology.',
                     'Percentage of degrees awarded in Homeland Security, Law Enforcement, Firefighting And Related Protective Services.',
                     'Percentage of degrees awarded in Public Administration And Social Service Professions.',
                     'Percentage of degrees awarded in Social Sciences.',
                     'Percentage of degrees awarded in Construction Trades.',
                     'Percentage of degrees awarded in Mechanic And Repair Technologies/Technicians.',
                     'Percentage of degrees awarded in Precision Production.',
                     'Percentage of degrees awarded in Transportation And Materials Moving.',
                     'Percentage of degrees awarded in Visual And Performing Arts.',
                     'Percentage of degrees awarded in Health Professions And Related Programs.',
                     'Percentage of degrees awarded in Business, Management, Marketing, And Related Support Services.',
                     'Percentage of degrees awarded in History.']
    columnNames = ['PCIP01',
                 'PCIP03',
                 'PCIP04',
                 'PCIP05',
                 'PCIP09',
                 'PCIP10',
                 'PCIP11',
                 'PCIP12',
                 'PCIP13',
                 'PCIP14',
                 'PCIP15',
                 'PCIP16',
                 'PCIP19',
                 'PCIP22',
                 'PCIP23',
                 'PCIP24',
                 'PCIP25',
                 'PCIP26',
                 'PCIP27',
                 'PCIP29',
                 'PCIP30',
                 'PCIP31',
                 'PCIP38',
                 'PCIP39',
                 'PCIP40',
                 'PCIP41',
                 'PCIP42',
                 'PCIP43',
                 'PCIP44',
                 'PCIP45',
                 'PCIP46',
                 'PCIP47',
                 'PCIP48',
                 'PCIP49',
                 'PCIP50',
                 'PCIP51',
                 'PCIP52',
                 'PCIP54'] # this and categoryVars are both in order
    # get the relative percentage points
    dfMajorsRanked = pd.DataFrame(columns=categoryVars)
    for group in state:
        if state[group].name == "": # if it is a group create tempDF and calculate actual row through there
            subDFMajors = pd.DataFrame(columns=categoryVars)
            for college in state[group].colleges:
                liMajors = list(data.loc[college, columnNames])
                subDFMajors.loc[len(subDFMajors)] = liMajors

            # if row contains instance of string, delete row
            x, y = subDFMajors.shape
            deleteRows = []
            for row in range(x):
                r = subDFMajors.iloc[row, :]
                if any(isinstance(val, str) for val in list(r)): # if true that their is a string in row
                    deleteRows.append(row)
            subDFMajors.drop(axis=0, inplace=True, labels=deleteRows)

            # find the mean in each category
            averageCateogry = list(subDFMajors.mean())
        else: # just find the numbers and append them
            averageCateogry = list(data.loc[state[group].name, columnNames])

        # append the (average) percentage each category to DF
        dfMajorsRanked.loc[len(dfMajorsRanked)] = averageCateogry
        dfMajorsRanked = dfMajorsRanked.rename(index={dfMajorsRanked.index.values[len(dfMajorsRanked)-1]:labels[group]}) # right here

    # find the top most for each and organize in a dataframe
    # plan is to iterate and determine top 5 in each row (group), then find each unique entry and make key from dictionary converting col names to categories
    topMajorCats = []
    for row in dfMajorsRanked.index:
        series = dfMajorsRanked.loc[row, :]
        seriesSorted = series.sort_values(ascending=False)
        names = list(seriesSorted.index)
        for item in names[0:4]: # top four majors in the category (four is better for the graph?)
            topMajorCats.append(item) # make sure the list is flat

    # determine the total number of unique degree types
    # use set to get the unique members of the list
    uniqueTopMajors = list(set(topMajorCats))

    # rename the columns to be shorter and create dictionary
    shortCategoryVars = [(i[33:-1]) for i in categoryVars]
    convLib = dict(zip(categoryVars, shortCategoryVars))


    # create list of unique majors short form
    graphMajorsShort = []
    for major in uniqueTopMajors:
        shortMajor = convLib[major]
        graphMajorsShort.append(shortMajor)
    # rename the columns to be shorter
    dfMajorsRanked.rename(columns = convLib, inplace=True)

    # plot it
    ax = dfMajorsRanked.loc[:, graphMajorsShort].T.plot.bar()

    # stylistic items
    ax.legend(bbox_to_anchor=(1, 1), handlelength=1)
    plt.title("Relative Degree Popularity Comparison", fontsize=16)
    plt.xlabel("Degree Type", fontsize=14)
    plt.ylabel("Relative Popularity", fontsize=14)

    # display plot
    st.pyplot(ax.plot())

    # write exact values to screen in DF form
    st.write(dfMajorsRanked.loc[:, graphMajorsShort].applymap(lambda x: round(x, 3)).to_html(), unsafe_allow_html=True)

    # offer to download the MultiBar_df
    st.download_button(label="Download Data", data=dfMajorsRanked.loc[:, graphMajorsShort].to_csv(),
                       file_name="relative_degree_comparison.csv")


# make graph comparing the act and SAT scores of university
def compare_ACT(state, data, labels): # RESUME HERE WITH DOWNLOADING
    # PRESENT ACT SCORES
    # Collect all data into data frame
    columns = ['ACTCM25', 'ACTCMMID', 'ACTCM75', 'ACTEN25', 'ACTENMID', 'ACTEN75',
               'ACTMT25', 'ACTMTMID', 'ACTMT75', 'ACTWR25', 'ACTWRMID', 'ACTWR75'] # order of cumulative, english, math, and writing
    dataACT = pd.DataFrame(columns=columns)
    for group in state:
        if state[group].name == "":  # if it is a group create tempDF and calculate actual row through there
            subACTdf = pd.DataFrame(columns=columns)
            for college in state[group].colleges: # for each college in larger group
                ACTScores = list(data.loc[college, columns]) # collect all ACT scores
                subACTdf.loc[len(subACTdf)] = ACTScores # append those scores

            # if row contains instance of string, delete row
            x, y = subACTdf.shape
            deleteRows = []
            for row in range(x):
                r = subACTdf.iloc[row, :]
                if any(isinstance(val, str) for val in list(r)):  # if true that their is a string in row
                    deleteRows.append(row)
            subACTdf.drop(axis=0, inplace=True, labels=deleteRows)

            # find the mean in each category
            averageScores = list(subACTdf.mean())
        else: # just a college
            averageScores = list(data.loc[state[group].name, columns])

        # append the (average) score each category to DF and rename row to the group
        dataACT.loc[len(dataACT)] = averageScores
        dataACT = dataACT.rename(index={dataACT.index.values[len(dataACT) - 1]: labels[group]})

    # create big graph
    fig, ax = plt.subplots()

    # plot each category and then college individually (ensures each is done correctly and in right location)
    # ENGLISH
    counter = 0 # track number of times something is graphed and where along the graph
    colorCounter = -1 # understand
    color = [] # keep track of when I have to graph each color in the color list
    colors = ['tab:blue', 'tab:green', 'tab:purple', 'tab:brown',
              'tab:olive', 'tab:cyan', 'tab:red'] # list of colors to choose from (automatically)
    for group in range(len(state)): # collect order I have to graph each color
        color.append(group)
    color = color * 4 # for the number of categories each group is graphed for
    try:
        for group in state: # for each group of colleges
            counter += 1
            colorCounter += 1
            try: # try to graph each group, but if can't leave it blank
                dist = [dataACT.loc[labels[group], "ACTEN25"]] * 1_000 + [dataACT.loc[labels[group], "ACTENMID"]] + [dataACT.loc[labels[group], "ACTEN75"]] * 1_000 # create distribution where the 25th and 75th percentiles are those scores
                b1 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True) # plot the group at the position
                for box in b1['boxes']:  # for the one box just plotted, change the face color of the box
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # MATH
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataACT.loc[labels[group], "ACTMT25"]] * 1_000 + [dataACT.loc[labels[group], "ACTMTMID"]] + [dataACT.loc[labels[group], "ACTMT75"]] * 1_000
                b2 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b2['boxes']:
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # WRITING
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataACT.loc[labels[group], "ACTWR25"]] * 1_000 + [dataACT.loc[labels[group], "ACTWRMID"]] + [dataACT.loc[labels[group], "ACTWR75"]] * 1_000
                b3 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b3['boxes']:

                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # Cumulative
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataACT.loc[labels[group], "ACTCM25"]] * 1_000 + [dataACT.loc[labels[group], "ACTCMMID"]] + [dataACT.loc[labels[group], "ACTCM75"]] * 1_000
                b4 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b4['boxes']:
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # set graph qualities
    plt.ylim(0,36) # 0 to max score
    plt.title("ACT Score and Subscore Comparison", size=16)
    plt.xlabel("ACT Category", size=14)
    plt.ylabel("Score", size=14)
    # change the x ticks
    start = (1+len(state))/2
    step = float(len(state) + 1)
    xTicks = [start, start+step, start+2*(step), start+3*(step)] # change the x ticks to be in the middle of each group
    plt.xticks(ticks=xTicks, labels=['English', 'Math', 'Writing', 'Cumulative']) # rename the xticks to identifyable names
    # setup legend
    # compile list of components and group names in order
    legendComponents = []
    groupLabels = []
    for groupNum, group in zip(range(len(labels)), labels):
        appention = Line2D([0], [0], color=colors[groupNum], lw=8)
        legendComponents.append(appention)
        groupLabels.append(labels[group])
    # create the legend
    ax.legend(legendComponents, groupLabels, bbox_to_anchor=(1, 1), handlelength=1)

    # display graph
    st.pyplot(plt.show())

    # display the data
    st.write(dataACT.applymap(lambda x: round(x, 2)).to_html(), unsafe_allow_html=True)

    # allow data to be downloaded
    st.download_button(label="Download Data", data=dataACT.to_csv(),
                       file_name="act_comparison_data.csv")


def compare_SAT(state, data, labels):
    # PRESENT SAT SCORES
    # Collect all data into data frame
    columns = ['SATVR25', 'SATVRMID', 'SATVR75', 'SATMT25', 'SATMTMID', 'SATMT75',
               'SATWR25', 'SATWRMID', 'SATWR75', 'SATCM25', 'SATCMMID',
               'SATCM75']  # order of critical reading, math, writing, cumulative
    dataSAT = pd.DataFrame(columns=columns)
    for group in state:
        if state[group].name == "":  # if it is a group create tempDF and calculate actual row through there
            subSATdf = pd.DataFrame(columns=columns)
            for college in state[group].colleges:  # for each college in larger group
                SATScores = list(data.loc[college, columns[:-3]])  # collect all available SAT scores (no cumulative)
                # calculate the cumulative scores and append
                cumScores = [SATScores[0]+SATScores[3], SATScores[1]+SATScores[4], SATScores[2]+SATScores[5]]
                SATScores = SATScores + cumScores
                # append all scores to df
                subSATdf.loc[len(subSATdf)] = SATScores

            # if row contains instance of string, delete row
            x, y = subSATdf.shape
            deleteRows = []
            for row in range(x):
                r = subSATdf.iloc[row, :]
                if any(isinstance(val, str) for val in list(r)):  # if true that their is a string in row
                    deleteRows.append(row)
            subSATdf.drop(axis=0, inplace=True, labels=deleteRows)

            # find the mean in each category
            averageScores = list(subSATdf.mean())
        else:  # just a college
            averageScores = list(data.loc[state[group].name, columns[:-3]])
            # find the cumulative scores
            cumScores = [averageScores[0] + averageScores[3], averageScores[1] + averageScores[4], averageScores[2] + averageScores[5]]
            averageScores = averageScores + cumScores

        # append the (average) score each category to DF and rename row to the group
        dataSAT.loc[len(dataSAT)] = averageScores
        dataSAT = dataSAT.rename(index={dataSAT.index.values[len(dataSAT) - 1]: labels[group]})

    # create big graph
    fig, ax = plt.subplots()

    # plot each category and then college individually (ensures each is done correctly and in right location)
    # ENGLISH
    counter = 0  # track number of times something is graphed and where along the graph
    colorCounter = -1  # understand
    color = []  # keep track of when I have to graph each color in the color list
    colors = ['tab:blue', 'tab:green', 'tab:purple', 'tab:brown',
              'tab:olive', 'tab:cyan', 'tab:red']  # list of colors to choose from (automatically)
    for group in range(len(state)):  # collect order I have to graph each color
        color.append(group)
    color = color * 4  # for the number of categories each group is graphed for
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataSAT.loc[labels[group], "SATVR25"]] * 1_000 + [dataSAT.loc[labels[group], "SATVRMID"]] + [dataSAT.loc[labels[group], "SATVR75"]] * 1_000  # create distribution where the 25th and 75th percentiles are those scores
                b1 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)  # plot the group at the position
                for box in b1['boxes']:  # for the one box just plotted, change the face color of the box
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # MATH
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataSAT.loc[labels[group], "SATMT25"]] * 1_000 + [dataSAT.loc[labels[group], "SATMTMID"]] + [dataSAT.loc[labels[group], "SATMT75"]] * 1_000
                b2 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b2['boxes']:
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # WRITING
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataSAT.loc[labels[group], "SATWR25"]] * 1_000 + [dataSAT.loc[labels[group], "SATWRMID"]] + [dataSAT.loc[labels[group], "SATWR75"]] * 1_000
                b3 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b3['boxes']:
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # Cumulative
    counter += 1
    try:
        for group in state:  # for each group of colleges
            counter += 1
            colorCounter += 1
            try:  # try to graph each group, but if can't leave it blank
                dist = [dataSAT.loc[labels[group], "SATCM25"]] * 1_000 + [dataSAT.loc[labels[group], "SATCMMID"]] + [dataSAT.loc[labels[group], "SATCM75"]] * 1_000
                b4 = plt.boxplot(dist, positions=[counter], widths=.6, patch_artist=True)
                for box in b4['boxes']:
                    box.set(facecolor=colors[color[colorCounter]])
            except:
                pass
    except:
        pass

    # set graph qualities
    plt.ylim(0, 1600)  # 0 to max score
    plt.title("SAT Score and Subscore Comparison", size=16)
    plt.xlabel("SAT Category", size=14)
    plt.ylabel("Score", size=14)
    # change the x ticks
    start = (1 + len(state)) / 2
    step = float(len(state) + 1)
    xTicks = [start, start + step, start + 2 * (step),
              start + 3 * (step)]  # change the x ticks to be in the middle of each group
    plt.xticks(ticks=xTicks,
               labels=['Critical Reading', 'Math', 'Writing', 'Cumulative'])  # rename the xticks to identifyable names
    # setup legend
    # compile list of components and group names in order
    legendComponents = []
    groupLabels = []
    for groupNum, group in zip(range(len(labels)), labels):
        appention = Line2D([0], [0], color=colors[groupNum], lw=8)
        legendComponents.append(appention)
        groupLabels.append(labels[group])
    # create the legend
    ax.legend(legendComponents, groupLabels, bbox_to_anchor=(1, 1), handlelength=1)

    # display graph
    st.pyplot(plt.show())

    # display the data
    st.write(dataSAT.applymap(lambda x: round(x, 2)).to_html(), unsafe_allow_html=True)

    # download option
    st.download_button(label="Download Data", data=dataSAT.to_csv(),
                       file_name="sat_comparison_data.csv")
