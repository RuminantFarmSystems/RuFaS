"""
RUFAS: Ruminant Farm Systems Model

File name: manure_handling.py

Description:
Description: Calculates nutrient losses and transformations during manure
                handling and updates separators. update_all() is called during
                the daily_manure_storage_routine() and it is the only method
                intended to be called from this file.

Author(s): William Donovan, wmdonovan@wisc.edu
"""


def update_all(pen, manure):
    """
    Description:
        Calls functions to calculate nutrient losses and transformations during
        manure handling.
        "pseudocode_manure_storage" MS.3

    Args:
        pen: an instance of the Pen class specified in pen.py representing
            the pen from which manure is being collected
        manure: an instance of the ManureStorage class specified in
            manure_storage.py
    """
    flush_water(pen, manure)
    N_loss(pen, manure)
    P_loss(pen, manure)
    K_loss(pen, manure)
    solids(pen, manure)


def flush_water(pen, manure):
    """
    Description:
        Calculates Flush Water Volume in the separator that processes the
        collected manure
        "pseudocode_manure_storage" MS.3.A

    Args:
        pen
        manure
    """

    pen.flush_water_volume = pen.raw_manure + pen.flush_water_daily + pen.bedding_washed
    manure.separators[pen.separator].flush_water_volume += pen.flush_water_volume


def N_loss(pen, manure):
    """
    Description:
        Updates Nitrogen mass in the separator from excreted manure
        "pseudocode_manure_storage" MS.3.B

    Args:
        pen
        manure
    """

    manure.separators[pen.separator].N = pen.N_excreted


def P_loss(pen, manure):
    """
    Description:
        Updates Phosphorus mass in the separator from excreted manure
"       pseudocode_manure_storage" MS.3.C

    Args:
        pen
        manure
    """

    manure.separators[pen.separator].P = pen.P_excreted


def K_loss(pen, manure):
    """
    Description:
        Updates Potassium mass in the separator from excreted manure
        "pseudocode_manure_storage" MS.3.D

    Args:
        pen
        manure
    """

    manure.separators[pen.separator].K = pen.K_excreted


def solids(pen, manure):
    """
    Description:
        Updates Total and Volatile Solids in the separator from excreted manure
        "pseudocode_manure_storage" MS.3.E

    Args:
        pen
        manure
    """
    pen.TS_loss = pen.flush_water_volume * pen.TS_loss_perc
    pen.VS_loss = pen.TS_loss * pen.VS_loss_perc

    manure.separators[pen.separator].TS += pen.TS_loss
    manure.separators[pen.separator].VS += pen.VS_loss
