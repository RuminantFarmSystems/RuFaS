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
###############################################################################


def update_all(storage):
    CP_loss(storage)

    NPN_loss(storage)

    update_CP(storage)


def CP_loss(storage):
    storage.CP_gas = storage.CP * storage.CP_gas_percent

    storage.CP_leachate = storage.CP * storage.CP_leachate_percent


def NPN_loss(storage):
    storage.NPN += storage.CP * storage.NPN_min_percent


def update_CP(storage):
    storage.CP_loss = storage.CP_gas + storage.CP_leachate
    storage.CP -= storage.CP_loss

    storage.DM -= storage.CP_loss
