################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: clustering_pen_grouping.py
Description: This file's main function is grouping(list, pens) (line 44) which returns
    a Dictionary of lists of cows, with the key being the pen those cows are
    assigned to based on nutritional requirments. This function is called in
    animal_management.py for each ration cycle if there are more than 7 pens in
    the input (>=2 pens for lactating cows)
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


def grouping(list, pens):
    '''Grouping algorithim that utilizes k-means clustering and takes an input
       that is a list of objects of class Cow (see cow.py) and groups them into
       exactly 1 of 14 different pens. This function returns a list of 14 lists
       of cow groupings (lists of objects of class Cow)

       Args: list = a list of lactating cows
             n = the number of pens allocated for lactating cows
    '''

    #############################################
    #Initial Data Manipulation
    #############################################
    #Each of the Following lists contain the following attributes corresponding
    #to the list of cows input in the grouping function
    RecDNED = []  #Required net energy density (Units= Mcal per kg of dry matter (DM) (Mcal/kg of DM))
    RecDMPD = []  #Required Metabolizing Protein Density (Units= g of crude protein per kg of DM (g/kg of DM))
    AVGMILK_kg = [] #Average milk produced
    for cow in list:
        RecDNED.append(cow.RecDNED)
        RecDMPD.append(cow.RecDMPD)
        AVGMILK_kg.append(cow._lactose_milk)

    #Creating a pandas dataframe with cow objects and relevant nutrition information
    Cow_nutr_df = pd.DataFrame()        #cow nutrition dataframe
    Cow_nutr_df['RecDNED'] = RecDNED
    Cow_nutr_df['RecDMPD'] = RecDMPD
    Cow_nutr_df['AVGMILK_kg'] = AVGMILK_kg
    Cow_nutr_df['Cow'] = list



    ##############################################
    #Using the various nutrition requirment variables to create assign a
    #percentile value to each cow
    ##############################################
    ##Grouping By Ranking Methology##
    RNKdat = Cow_nutr_df[["RecDNED", "RecDMPD", "AVGMILK_kg"]] #Rank Dataframe to creat percentile vector
    RNKdat = RNKdat.dropna()

    ScDNED = [] #normalized list of the RecDNED list
    ScDMPD = [] #normalized list of the RecDNED list
    ScMilk = [] #normalized list of the AVGMILK_kg
    RecDNED = RNKdat['RecDNED'].to_list()
    RecDMPD = RNKdat['RecDMPD'].to_list()
    AVGMILK_kg = RNKdat['AVGMILK_kg'].to_list()

    #Normalizing Vectors RecDNED, RecDMPD, AVGMILK_kg
    ScDNED = norm(RecDNED).tolist()
    ScDMPD = norm(RecDMPD).tolist()
    ScMilk = norm(AVGMILK_kg).tolist()

    #Adding the  normalized vectors to the RNKdat dataframe
    n = len(RNKdat.columns)
    RNKdat.insert(n, 'ScDNED', ScDNED)
    RNKdat.insert(n +1, 'ScDMPD', ScDMPD)
    RNKdat.insert(n +2, 'ScMilk', ScMilk)
    #Creating sum of Std Nutrient Requirment values
    std = RNKdat[['ScDNED', 'ScDMPD', 'ScMilk']].sum(axis= 1, skipna = True).to_list()
    RNKdat.insert(n +3, 'std', std)

    #Creating A Nutrient Requirment Percentile Vector (with respect to all cows)
    Percentile = []
    Percentile = percentile_list(std)
    n = len(RNKdat.columns)
    RNKdat.insert(n, 'Percentile', Percentile)
    Cow_nutr_df['Percentile'] = Percentile
    Cow_nutr_df['Percentile'] = 1 - Cow_nutr_df['Percentile']


    #############################################
    ###Grouping###
    #grouping by nutrient requirment percentile percentile and num of stalls in each pen
    #############################################
    Total_Cows = len(list)            #Total Number of Cows
    Index = {4: 0}                  #Cuttoff values for percentiles for each pen
    #Creating a list of percentile partitions for grouping
    for pen in pens:
        Index[pen.id] = (pen.num_stalls / Total_Cows) + Index[(pen.id - 1)]
        if Index[pen.id] > 1:
            Index[pen.id] = 1
    Pen = []                           #List of Pen Assignment to be added to the dataframe
    Percentile = RNKdat['Percentile'].to_list()
    #Assiging Pen number to list based on percentile
    for i in range(len(Percentile)):
        key = 5
        group = 0
        while (Percentile[i] <= Index[key-1] or Percentile[i] > Index[key]):
            group = key
            key += 1
        Pen.append(key)
    #Adding the Pen assignment vector to the DataFrame
    n = len(RNKdat.columns)
    RNKdat.insert(n, 'Pen', Pen)
    Cow_nutr_df["Pen"] = Pen

    #############################################
    ###Pen Summary Output###
    #Sorting The Dataframe By Pen
    #Returning Dicionary of Lists of cow objects, with keys corresponding to Pen IDs
    #############################################
    Pendat = Cow_nutr_df.sort_values(by = 'Pen', ascending = True)
    #creating a list of values that keep track of the index for the start of each pen in the ID list#
    seperating_index = [0]
    Pen = Pendat['Pen'].to_list()
    Cow = Pendat['Cow'].to_list()
    for i in range(len(Pen)):
        if (i != (len(Pen)-1) and Pen[i] != Pen[i+1]):
            seperating_index.append(i+1)
    seperating_index.append(len(Pen))
    #Creating Dictionary wit Lists of ID's for each pen (5,6,7...)#
    Grouping_Data = {}
    key = 5
    for i in range(len(seperating_index) - 1):
        group = Cow[seperating_index[i] : seperating_index[i+1]]
        Grouping_Data[key] = group
        key +=1
    #returning the Dictionary of groupings
    return(Grouping_Data)
################################################################################
