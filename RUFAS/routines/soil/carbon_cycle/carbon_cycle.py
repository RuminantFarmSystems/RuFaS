"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_cycle.py

Author(s): William Donovan, wmdonovan@wisc.edu,
           Jacob Johnson, jacob8399@gmail.com

Description: Carbon Cycle driver class.
"""


def update_all(soil):
    """
    Description:
        This function calls all the necessary functions to update information related
        to the carbon cycle. The order in which each method is called is significant.

    Args:
        soil
    """

    # residue from annual crops
    soil.residue_DM = soil.residue * (1 - soil.plant_moisture)

    # residue partitioning

