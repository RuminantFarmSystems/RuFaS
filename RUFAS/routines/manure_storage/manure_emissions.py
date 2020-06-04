"""
RUFAS: Ruminant Farm Systems Model

File name: manure_emissions.py

Description:

Author(s): William Donovan, wmdonovan@wisc.edu
"""


def update_all(storage, manure):
    methane(storage, manure)


def methane(storage, manure):
    manure.CH4_emissions += storage.VS * manure.Bo * manure.MCF * manure.MS * \
                            manure.m3 * manure.CH4_collection_efficiency
