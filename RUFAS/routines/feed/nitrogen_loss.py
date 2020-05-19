"""
RUFAS: Ruminant Farm Systems Model
File name: nitrogen_loss.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the nitrogen loss during harvest, storage, and feed out.
             The only function meant to be used outside of this file is the
             update_all() function. The other functions are meant to serve as
             helper functions within this file.

Feed attribute definitions:

Feed values updated by update_all():

"""


def update_all(storage):
    """
    Description:
        The only external function call. Runs the nitrogen loss sub-module
    Args:
        storage: the storage receptacle for which loss is being calculated
    """
    CP_loss(storage)

    NPN_loss(storage)

    update_CP(storage)


def CP_loss(storage):
    """
    Description:
        Crude protein loss to gas and leaching
    Args:
        storage
    """

    storage.CP_gas = storage.CP * storage.CP_gas_percent

    storage.CP_leachate = storage.CP * storage.CP_leachate_percent


def NPN_loss(storage):
    """
    Description:
        Non-Protein-Nitrogen loss
        TODO: Value never used
    Args:
        storage
    """

    storage.NPN += storage.CP * storage.NPN_min_percent


def update_CP(storage):
    """
    Description:
        Account for crude protein loss in relevant pools
    Args:
        storage
    """
    storage.CP_loss = storage.CP_gas + storage.CP_leachate

    storage.CP -= storage.CP_loss
    storage.DM -= storage.CP_loss
