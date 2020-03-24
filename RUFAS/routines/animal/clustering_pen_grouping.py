################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: clustering_pen_grouping.py
Description: This file's main function is grouping(list) (line 54) which returns
    a 2D matrix (or list of lists) with each list in the matrix being a pen
    grouping of cows based on nutritional requirments. This function is called in
    animal_management.py for each ration cycle if there are more than 7 pens in
    the input.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
'''
################################################################################
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
import matplotlib
import csv
import xlsxwriter
import time as timer


def norm(x):
    '''Helper function that
       normalizes a list of values and returns that normalized list
    '''
    x = np.array(x)
    if max(x) != min(x):
        normalized = (x - min(x)) / (max(x) - min(x))
        return normalized
    else:
        return x

def percentile_list(l):
    '''Helper function that returns a list of percentiles corresponding
    to its matching value in the original list
    '''
    percentile_list = []
    for e in l:
        x = percentileofscore(l, e)
        percentile_list.append(x/100)
    return(percentile_list)


def grouping(list):
    '''Grouping algorithim that utilizes k-means clustering and takes an input
       that is a list of objects of class Cow (see cow.py) and groups them into
       exactly 1 of 14 different pens. This function returns a list of 14 lists
       of cow groupings (lists of objects of class Cow)
    '''


#############################################
#Initial Data Manipulation
#############################################
    #Cow ID number
    ID = []
    #
    weekn = []
    #Days In Milk
    DIM = []
    #Lactation Number
    LACT = []
    RecDNED = []
    RecDMPD = []
    #Avergae Milk Production
    AVGMILK_kg = []

    for cow in list:
        ID.append(cow.ID)
        weekn.append(cow.weekn)
        DIM.append(cow._days_in_milk)
        LACT.append(cow.LACT)
        RecDNED.append(cow.RecDNED)
        RecDMPD.append(cow.RecDMPD)
        AVGMILK_kg.append(cow.AVGMILK_kg)


    Cowrd = pd.DataFrame()
    Cowrd['ID'] = ID
    Cowrd['weekn'] = weekn
    Cowrd['DIM'] = DIM
    Cowrd['LACT'] = LACT
    Cowrd['RecDNED'] = RecDNED
    Cowrd['RecDMPD'] = RecDMPD
    Cowrd['AVGMILK_kg'] = AVGMILK_kg

    mygroups = [2, 3, 4, 6, 7, 8, 9, 22, 23, 24, 25, 26, 27, 28]

    #Aggregate the data for nutritional requirements per cow per week (using mean metric)
    AggNGdata = Cowrd.groupby(['weekn', 'ID']).mean()
    AggNGdata = AggNGdata.drop(columns = ['DIM', 'LACT'])
    #Data grouped using the "maximum" metric
    MergData = Cowrd[['ID', 'DIM', 'LACT', 'weekn']]
    MergData = MergData.groupby(['weekn', 'ID']).max()
    #Joining the two grouped datasets into one
    NGdata = AggNGdata.join(MergData, how = 'left' )


    #############################################
    #Categorizing Lactation number#
    #############################################
    LACT = NGdata['LACT'].tolist()
    LACTcat = []

    for i in range(len(LACT)):
        if (LACT[i] == 1):
            LACTcat.append(1)
        else:
            LACTcat.append(2)
    n = len(NGdata.columns)
    NGdata.insert(n, 'LACTcat', LACTcat)
    ##############################################
    #Setting the number of nutritional groups and number of cows per group
    ##############################################
    #Ordering by weekn, LACTcat, and DIM
    NGdata = NGdata.sort_values(by = ['weekn', 'LACTcat','DIM'], ascending = [True, True, True])

    ###Creating Rank Array###
    LACTcat = NGdata['LACTcat'].tolist()
    NGdata_1 = NGdata.reset_index()
    weeknlist = NGdata_1['weekn'].tolist()
    weeknn = []
    for num in weeknlist:
        if num not in weeknn:
            weeknn.append(num)

    rank = []
    for n in weeknn:
        u = 1
        v = 1
        for i in range(len(weeknlist)):
            if (n == weeknlist[i] and LACTcat[i] == 1):
                rank.append(u)
                u += 1
            elif (n == weeknlist[i] and LACTcat[i] == 2):
                rank.append(v)
                v += 1
    n = len(NGdata.columns)
    NGdata.insert(n, 'rank', rank)

    ##Size per pen category##
    SFPenP=148 #Size Fresh Pens Pimiparous
    SFPenM=148 #Size Fresh Pens Multiparous
    SEPenP=148 #Size Early Pens Pimiparous
    SEPenM=148 #Size Early Pens Multiparous
    SPPenP=444 #Size Peak Pens Pimiparous
    SPPenM=444 #Size Peak Pens Multiparous

    #Adding column DIMcat (Days in Milk Categorization)
    ## 1=Fresh, 2=Early, 3=Peak, 4=Late##
    LACTcat = NGdata['LACTcat'].tolist()
    DIMcat = []

    for i in range(len(LACTcat)):
        if (LACTcat[i] == 1 and rank[i] <= SFPenP):
            DIMcat.append(1)
        elif (LACTcat[i] == 2 and rank[i] <=SFPenP):
            DIMcat.append(1)
        elif (LACTcat[i] == 1 and rank[i] > SFPenP and rank[i] <= SFPenP + SEPenP):
            DIMcat.append(2)
        elif (LACTcat[i] == 2 and rank[i] > SFPenM and rank[i] <= SFPenM + SEPenM):
            DIMcat.append(2)
        elif (LACTcat[i] == 1 and rank[i] > SFPenP + SEPenP and rank[i] <= SFPenP+SEPenP+SPPenP):
            DIMcat.append(3)
        elif (LACTcat[i] == 2 and rank[i] > SFPenM + SEPenM and rank[i] <= SFPenM+SEPenM+SPPenM):
            DIMcat.append(3)
        else:
            DIMcat.append(4)
    n = len(NGdata.columns)
    NGdata.insert(n, 'DIMcat', DIMcat)
    ##Grouping By Ranking Methology##
    RNKdat = NGdata[["RecDNED", "RecDMPD", "AVGMILK_kg","DIM", "DIMcat", "LACTcat"]]
    RNKdat = RNKdat.dropna()

    #Clustering By ranking
    index = [0]
    DIMcat = RNKdat['DIMcat'].to_list()
    for i in range(len(DIMcat) - 1):
        if DIMcat[i] != DIMcat[i+1]:
            index.append(i + 1)
    index.append(len(DIMcat))

    ScDNED = []
    ScDMPD = []
    ScMilk = []
    RecDNED = RNKdat['RecDNED'].to_list()
    RecDMPD = RNKdat['RecDMPD'].to_list()
    AVGMILK_kg = RNKdat['AVGMILK_kg'].to_list()
    #Normalizing Vectors RecDNED, RecDMPD, AVGMILK_kg
    if len(RecDNED) > 0:
        for i in range(len(index) - 1):
            x = norm(RecDNED[index[i] : index[i+1]]).tolist()
            y = norm(RecDMPD[index[i] : index[i+1]]).tolist()
            z = norm(AVGMILK_kg[index[i] : index[i+1]]).tolist()
            ScDNED = ScDNED + x
            ScDMPD = ScDMPD + y
            ScMilk = ScMilk + z
        #Adding the vectors to the RNKdat dataframe
        n = len(RNKdat.columns)
        RNKdat.insert(n, 'ScDNED', ScDNED)
        RNKdat.insert(n +1, 'ScDMPD', ScDMPD)
        RNKdat.insert(n +2, 'ScMilk', ScMilk)
        std = RNKdat[['ScDNED', 'ScDMPD', 'ScMilk']].sum(axis= 1, skipna = True).to_list()
        RNKdat.insert(n +3, 'std', std)

        #Creating Percentile Vector
        Percentile = []
        for i in range(len(index) - 1):
            x = percentile_list(std[index[i] : index[i+1]])
            Percentile = Percentile + x
        n = len(RNKdat.columns)
        RNKdat.insert(10, 'Percentile', Percentile)

        #Grouping By percentile
        ## 1=Firstlact, 2=Mature##
        ## 1=TransitionFresh, 2=Fresh, 3=Picklact, 4=Late lactation##
        index2 = [0]
        for i in range(len(weeknlist) -1):
            if weeknlist[i] != weeknlist[i+1]:
                index2.append(i+1)
        index2.append(len(weeknlist))

        NGgroup = []
        LACTcat = RNKdat['LACTcat'].to_list()
        DIMcat = RNKdat['DIMcat'].to_list()
        Percentile = RNKdat['Percentile'].to_list()
        for i in range(len(index2) - 1):
            for ii in range(index2[i], index2[i+1]):
                if (LACTcat[ii] == 1 and DIMcat[ii] == 1):
                    NGgroup.append(28)
                elif (LACTcat[ii] == 2 and DIMcat[ii] == 1):
                    NGgroup.append(27)
                elif (LACTcat[ii] == 1 and DIMcat[ii] == 2):
                    NGgroup.append(25)
                elif (LACTcat[ii] == 2 and DIMcat[ii] == 2):
                    NGgroup.append(26)
                elif (LACTcat[ii] == 2 and DIMcat[ii] == 3 and Percentile[ii] <= 0.3333):
                    NGgroup.append(22)
                elif (LACTcat[ii] == 2 and DIMcat[ii] == 3 and 0.3333 < Percentile[ii] <= 0.6666):
                    NGgroup.append(23)
                elif (LACTcat[ii] == 2 and DIMcat[ii] == 3 and Percentile[ii] > 0.6666):
                    NGgroup.append(24)
                elif (LACTcat[ii] == 1 and DIMcat[ii] == 3 and Percentile[ii] <= 0.3333):
                    NGgroup.append(7)
                elif (LACTcat[ii] == 1 and DIMcat[ii] == 3 and 0.3333 < Percentile[ii] <=0.6666):
                    NGgroup.append(8)
                elif (LACTcat[ii] == 1 and DIMcat[ii] == 3 and Percentile[ii] > 0.6666):
                    NGgroup.append(9)
                elif ((LACTcat[ii] == 1 or LACTcat[ii] == 2) and DIMcat[ii] == 4 and Percentile[ii] <= 0.25):
                    NGgroup.append(2)
                elif ((LACTcat[ii] == 1 or LACTcat[ii] == 2) and DIMcat[ii] == 4 and 0.25 < Percentile[ii] <=0.50):
                    NGgroup.append(3)
                elif ((LACTcat[ii] == 1 or LACTcat[ii] == 2) and DIMcat[ii] == 4 and 0.50 < Percentile[ii] <=0.75):
                    NGgroup.append(4)
                elif ((LACTcat[ii] == 1 or LACTcat[ii] == 2) and DIMcat[ii] == 4 and Percentile[ii] > 0.75):
                    NGgroup.append(6)
                else:
                    NGgroup.append(0)
        n = len(RNKdat.columns)
        RNKdat.insert(n, 'NGgroup', NGgroup)


        Clustoutp = RNKdat['NGgroup']
        NGdata = NGdata.join(Clustoutp, how = 'left')

        ######Pen Summary#######
        PenDat = NGdata[['DIMcat', 'LACTcat', 'NGgroup']]
        LACTcategory = []
        LACTcat = PenDat['LACTcat'].to_list()
        for x in LACTcat:
            if (x == 1):
                LACTcategory.append('Primiparous')
            else:
                LACTcategory.append('Multiparous')
        DIMcategory = []
        DIMcat = PenDat['DIMcat'].to_list()
        for x in DIMcat:
            if (x == 1):
                DIMcategory.append('Fresh')
            elif (x == 2):
                DIMcategory.append('Early')
            elif (x == 3):
                DIMcategory.append('Peak')
            else:
                DIMcategory.append('Late')
        n = len(PenDat.columns)
        PenDat.insert(n, 'LACTcategory', LACTcategory)
        PenDat.insert(n+1, 'DIMcategory', DIMcategory)
        PenDat = PenDat.dropna()

        col_num = PenDat.shape[0]
        Freq = [1] * col_num
        PenDat.insert(n+2, 'Freq', Freq)
        df = PenDat.reset_index()

        PenDat = df.groupby(['DIMcategory', 'LACTcategory', 'NGgroup', 'weekn', 'ID']).count()
        PenDat = PenDat['Freq']
        PenDat = PenDat.reset_index()
        PenDat= PenDat[['weekn', 'NGgroup', 'LACTcategory', 'DIMcategory', 'Freq', 'ID']]
        Grouping_Data = PenDat[['ID', 'NGgroup']]

        ID = Grouping_Data['ID'].to_list()
        NGgroup = Grouping_Data['NGgroup'].to_list()
        Grouping_Data = [ID, NGgroup]
        return(Grouping_Data)

################################################################################
