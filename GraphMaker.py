# imports
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import math
import streamlit as st

# determining group (for efficiency testing)
def ChooseGroup(df, region, state, admission, status, size):
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
        cost_per_income_level_comp(state, df, labels, userLabels)
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

# comparing the cost at each interval
def cost_per_income_level_comp(state, data, labels, userLabels): # fix ordering problem here and group listing
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
        st.text(f"{group}: {roundNumb}")

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
            tempList = [float(i) for i in tempList if i.isnumeric()] # removed suppressed values
            med_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "LO_INC_DEBT_MDN"])
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
            low_inc_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "MD_INC_DEBT_MDN"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
            md_inc_debt = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "HI_INC_DEBT_MDN"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
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
        st.text(f"{group}: {roundNumb}")

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
            tempList = [float(i) for i in tempList if i.isnumeric()] # removed suppressed values
            debt_90 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P75"])
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
            debt_75 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P25"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
            debt_25 = stat.mean([item for item in tempList if not (math.isnan(item)) == True])
        except:
            pass
        try:
            tempList = list(df.loc[:, "CUML_DEBT_P10"])  # assume dependent students
            tempList = [i for i in tempList if type(i) != float]  # remove nans
            tempList = [float(i) for i in tempList if i.isnumeric()]
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
        st.text(f"{group}: {roundNumb}")

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
            tempList = [float(i) for i in tempList if i.isnumeric()]  # removed suppressed values
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
            tempList = [float(i) for i in tempList if i.isnumeric()]
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
        st.text(f"{group}: {roundNumb}")


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
            tempList = [float(i) for i in tempList if i.isnumeric()]  # removed suppressed values
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
            tempList = [float(i) for i in tempList if i.isnumeric()]
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
        st.text(f"{group}: {roundNumb}")

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
            tempList = [float(i) for i in tempList if i.isnumeric()]  # removed suppressed values
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
            tempList = [float(i) for i in tempList if i.isnumeric()]
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

    # remove spaces from keys and replace
    oldKeys = graphDict.keys()
    for entry in oldKeys:
        newKey = entry.strip()
        graphDict[entry] = graphDict[newKey]

    # make the webpage say the numbers
    for group in graphDict:
        roundNumb = [round(i, 2) for i in graphDict[group]]
        st.text(f"{group}: {roundNumb}")