# """
# RUFAS: Ruminant Farm Systems Model
#
# File name: percolation.py
#
# Author(s): William Donovan, wmdonovan@wisc.edu
#
# Description: This module contains the necessary functions for calculating and
#              updating water percolation on a given day. Currently the only
#              function meant to be used outside of this file is the update_all()
#              function. The other functions are meant to serve as helper
#              methods within this file.
#
# Soil attribute definitions
#
#     percolation = amount of water that percolates to the underlying soil layer (mm H2O)
#
#     t = time step (24h)
#
#     TT = travel time for percolation (h)
#
#     K_sat = saturated hydraulic conductivity (mm/h)
# """
#
# from math import exp
#
#
# def update_all(soil):
#     """
#     Definition:
#         This function calls all the necessary functions to update information related
#         to percolation
#
#     Args:
#         soil: an instance of the Soil class specified in soil.py
#     """
#
#     calc_daily_percolation(soil)
#
#
# def calc_daily_percolation(soil):
#     """
#     Definition:
#         Calculates daily percolation as a function of the water available for
#         percolation (SW_perc) in a soil layer.
#         "pseudocode_soil" S.2.C.1/2
#
#     Args:
#         soil
#     """
#     for layer in soil.soil_layers:
#         SAT = layer.sat_water
#
#         SW = layer.soil_water
#         FC = layer.fc_water
#         WP = layer.wilting_water
#
#         SW_percolation = 0.0
#         if SW > FC:
#             SW_percolation = SW - FC
#
#         K_sat = layer.k_sat
#
#         # Travel Time for each soil layer
#         # "pseudocode_soil" S.2.C.2
#         TT = (SAT - FC) / K_sat
#         layer.TT = TT
#
#         t = 24
#
#         exp_part = exp((-t) / layer.TT)
#         percolation = SW_percolation * (1 - exp_part)
#         layer.percolation = min(SW - WP, percolation)

from typing import List, Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based on the section 'Percolation' (2:3.2) in SWAT
"""


class Percolation:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()

    def percolate(self, available_water_capacities: List[float]) -> None:
        """executes percolation of excess water in each layer of soil profile to the layer directly beneath it

        Args:
            available_water_capacities: list of the available water capacities of each layer of the soil profile, each
                expressed as a fraction of the total soil volume

        SWAT Reference: sections 2:3.1 and 2
        """
