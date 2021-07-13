"""
RUFAS: Ruminant Farm Systems Model

File name: manure_emissions.py

Description:
Description: Calculates nutrient losses and transformations during manure
                separation and updates storage receptacles. update_all() is
                called during the daily_manure_storage_routine() and it is the
                only method intended to be called from this file.

Author(s): William Donovan, wmdonovan@wisc.edu
"""


def update_all(separator, manure):
    """
    Description:
        Calls functions to calculate nutrient losses and transformations during
        manure separation.
        "pseudocode_manure_storage" MS.4

    Args:
        separator: an instance of the Separator class defined in
            manure_storage.py
        manure: an instance of the ManureStorage class defined in
            manure_storage.py
    """
    effluent_liquid(separator)
    effluent_solid(separator)
    update_storage(separator, manure)


def effluent_liquid(separator):
    """
    Description:
        Calculate liquid nutrient content of the separator
        "pseudocode_manure_storage" MS.4.A

    Args:
        separator
    """

    separator.TS_liquid = separator.TS - (separator.TS * separator.TS_removal_efficiency)
    separator.VS_liquid = separator.VS - (separator.VS * separator.VS_removal_efficiency)
    separator.N_liquid = separator.N - separator.N * separator.N_removal_efficiency
    separator.P_liquid = separator.P - separator.P * separator.P_removal_efficiency
    separator.K_liquid = separator.K - separator.K * separator.K_removal_efficiency


def effluent_solid(separator):
    """
    Description:
        Update solid nutrient content of the separator
        "pseudocode_manure_storage" MS.4.B

    Args:
        separator
    """

    separator.TS -= separator.TS_liquid
    separator.TS_DM_effluent = separator.TS * separator.TS_DM_effluent_rate
    separator.TS -= separator.TS_DM_effluent

    separator.VS -= separator.VS_liquid
    separator.N -= separator.N_liquid
    separator.P -= separator.P_liquid
    separator.K -= separator.K_liquid


def update_storage(separator, manure):
    """
    Description:
        Update solid and liquid nutrient contents of the storage receptacle
        "pseudocode_manure_storage" MS.4.C

    Args:
        separator
        manure
    """
    storage = manure.storage[separator.storage_system]

    storage.TS += separator.TS
    storage.TS_liquid += separator.TS_liquid

    storage.VS += separator.VS
    storage.VS_liquid += separator.VS_liquid

    storage.N += separator.N
    storage.N_liquid += separator.N_liquid

    storage.P += separator.P
    storage.P_liquid += separator.P_liquid

    storage.K += separator.K
    storage.K_liquid += separator.K_liquid

    storage.CH4 += separator.CH4

    storage.WIP += separator.WIP
    storage.WOP += separator.WOP
