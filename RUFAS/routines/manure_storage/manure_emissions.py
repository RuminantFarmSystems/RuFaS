"""
RUFAS: Ruminant Farm Systems Model

File name: manure_emissions.py

Description:

Author(s): William Donovan, wmdonovan@wisc.edu
"""


def update_all(storage, manure):
    methane(storage, manure)
    WIP_WOP_frac(storage)


def methane(storage, manure):
    manure.CH4_emissions = storage.VS * manure.Bo * manure.MCF * manure.MS * manure.m3


def WIP_WOP_frac(storage):
    storage.WIP_frac = 0 if (storage.TS + storage.VS == 0) else (storage.WIP / (storage.TS + storage.VS))
    storage.WOP_frac = 0 if (storage.TS + storage.VS == 0) else (storage.WOP / (storage.TS + storage.VS))
