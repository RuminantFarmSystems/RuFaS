'''
RUFAS: Ruminant Farm Systems Model

File name: residue.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating soil residue on a given day. The only method meant to be
             called outside this function is update_all. All other methods are
             helper functions

Soil attribute definitions

    residue = biomass left behind on the soil after harvest or decay

    dResidue = the difference between biomass and harvest yield used to
                calculate residue

    decayRate = rate of biomass decay for a given soil profile

Crop attribute definitions

    harvest_date = date of a plant's harvest

    biomass_actual = crop biomass on a given day

    yield_actual = harvest yield

Soil values updated by calling update_all():

    residue

'''

###############################################################################


#
# Calls the necessary functions for updating values pertaining to residue
#
def update_all(soil, crop, time):
    update_residue(soil, crop, time)


#
# Calculates change in residue on a given day. If there is a crop growing and
# it is that crop's harvest date, dResidue is calculated as the difference
# between biomass before harvest and the harvest yield
#
def update_residue(soil, crop, time):
    crop_type = crop.crops_list["corn"]
    soil.residue *= (1 - soil.decayRate)
    if time.day == crop_type.harvest_date:
        dResidue = crop_type.biomass_actual - crop_type.yield_actual
        soil.residue += dResidue