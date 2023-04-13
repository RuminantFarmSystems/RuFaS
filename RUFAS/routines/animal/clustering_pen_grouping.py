################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: clustering_pen_grouping.py
Description: This file's main function is grouping(list, pens) (line 44) which
    returns a Dictionary of lists of cows, with the key being the pen those cows
    are assigned to based on nutritional requirements. This function is called
    in animal_management.py for each ration cycle if there are more than 7 pens
    in the input (>=2 pens for lactating cows). Based on algorithm developed by
    Jorge Barrientos (jab924@cornell.edu).
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
import math

################################################################################
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore


def norm(x):
    """
        Helper function to normalize a list of values and returnthat normalized
        list.

        Args:
            x: A list of values
    """
    x = np.array(x)
    if max(x) != min(x):
        normalized = (x - min(x)) / (max(x) - min(x))
        return normalized
    else:
        return x


def percentile_list(l):
    """
        Helper function that returns a list of percentiles corresponding
        to its matching value in the original list.

        Args:
            l: a list of values
    """
    perc_list = []
    for e in l:
        x = percentileofscore(l, e)
        perc_list.append(x / 100)
    return perc_list


def grouping(cow_list, pens, stocking_density):
    """
        Grouping algorithm that utilizes k-means clustering and takes an input
        that is a list of objects of class cow (see cow.py) and a list of
        pen objects (from pen.py), and then groups the lactating cows into the
        available pens based on their nutritional requirements relative to the
        rest of the cows.

        Args:
            cow_list: a list of lactating cows
            pens: the number of pens allocated for lactating cows
            stocking_density: The required stocking density to group all cows
    """

    #########################
    # Data manipulation and pen sorting
    # Each of the following lists contain the following attributes corresponding
    # to the list of cows input in the grouping function
    #########################
    # Required net energy density (Units= Mcal per kg of dry matter (DM) (Mcal/kg of DM))
    DNED_req = []
    # Required Metabolizing Protein Density (Units= g of crude protein per kg of DM (g/kg of DM))
    DMPD_req = []
    # Average milk produced (kg)
    milk_avg = []

    for cow in cow_list:
        DNED_req.append(cow.DNED_req)
        DMPD_req.append(cow.DMPD_req)
        milk_avg.append(cow.estimated_daily_milk_produced)

    # Create a pandas data frame with cow objects and relevant nutrition information
    cow_nutr_df = pd.DataFrame()  # cow nutrition data frame
    cow_nutr_df['DNED_req'] = DNED_req
    cow_nutr_df['DMPD_req'] = DMPD_req
    cow_nutr_df['milk_avg'] = milk_avg
    cow_nutr_df['cow'] = cow_list

    # Use the various nutrition requirement variables to create and assign a
    # percentile value to each cow
    # Grouping By Ranking Methodology
    rank_data = cow_nutr_df[["DNED_req", "DMPD_req", "milk_avg"]]  # Rank data frame to create percentile vector
    rank_data = rank_data.dropna()

    DNED_req = rank_data['DNED_req'].to_list()
    DMPD_req = rank_data['DMPD_req'].to_list()
    milk_avg = rank_data['milk_avg'].to_list()

    # Normalize Vectors DNED_req, DMPD_req, milk_avg
    sc_DNED = norm(DNED_req).tolist()
    sc_DMPD = norm(DMPD_req).tolist()
    sc_milk = norm(milk_avg).tolist()

    # Add the normalized vectors to the rank_data data frame
    n = len(rank_data.columns)
    rank_data.insert(n, 'sc_DNED', sc_DNED)
    rank_data.insert(n + 1, 'sc_DMPD', sc_DMPD)
    rank_data.insert(n + 2, 'sc_milk', sc_milk)

    # Sum standard nutrient requirement values
    std = rank_data[['sc_DNED', 'sc_DMPD', 'sc_milk']].sum(axis=1, skipna=True).to_list()
    rank_data.insert(n + 3, 'std', std)

    # Create a nutrient requirement percentile vector (with respect to all cows)
    percentile = percentile_list(std)

    rank_data.insert(n + 4, 'percentile', percentile)
    cow_nutr_df['percentile'] = percentile
    cow_nutr_df['percentile'] = 1 - cow_nutr_df['percentile']

    # Group by nutrient requirement percentile percentile and num of stalls in
    # each pen
    # total number of cows
    num_cows = len(cow_list)
    # cutoff values for percentiles for each pen
    index = {-1: 0}

    # Create a list of percentile partitions for grouping
    key = 0
    for pen in pens:
        #filling pens based on input stocking density
        index[key] = (round(pen.num_stalls*stocking_density +0.5) / num_cows) + index[(key - 1)]
        if index[key] > 1:
            index[key] = 1
        key += 1

     # list of pen assignments to be added to the data frame
    pen_assignment = []
    percentile = rank_data['percentile'].to_list()

    # Adding pen_assignment number to list based on percentile
    for i in range(len(percentile)):
        key = 0
        while percentile[i] <= index[key - 1] or (
                percentile[i] > index[key] and not math.isclose(percentile[i], index[key], rel_tol=1e-09)):
            key += 1
        pen_assignment.append(key)

    # Adding the pen_assignment assignment vector to the DataFrame
    n = len(rank_data.columns)
    rank_data.insert(n, 'pen_assignment', pen_assignment)
    cow_nutr_df["pen_assignment"] = pen_assignment

    #########################
    # Pen assignment summary
    # Sort the data frame by pen assignment and return a dictionary of
    # lists of cow objects, with keys corresponding to pen IDs
    #########################
    pen_data = cow_nutr_df.sort_values(by='pen_assignment', ascending=True)
    # Creating a list of values that keep track of the index for the start of each pen in the ID list
    separating_index = [0]
    pen_assignment = pen_data['pen_assignment'].to_list()
    cow = pen_data['cow'].to_list()
    for i in range(len(pen_assignment)):
        if i != (len(pen_assignment) - 1) and pen_assignment[i] != pen_assignment[i + 1]:
            separating_index.append(i + 1)
    separating_index.append(len(pen_assignment))

    # Create Dictionary with lists of ID's for each pen (5,6,7...)
    grouping_data = {}
    key = 0

    for i in range(len(separating_index) - 1):
        group = cow[separating_index[i]: separating_index[i + 1]]
        grouping_data[key] = group
        key += 1

    # returning the dictionary of groupings
    return grouping_data
