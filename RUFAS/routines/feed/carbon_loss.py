"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_loss.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the carbon loss during harvest, storage, and feed out.
             The only function meant to be used outside of this file is the
             update_all() function. The other functions are meant to serve as
             helper functions within this file.

Feed attribute definitions:

Feed values updated by update_all():

"""


def update_all(storage):
    """
    Description:
        The only external function call. Runs the carbon loss sub-module
    """

    harvest_loss(storage)

    storage_loss(storage)

    feed_out_loss(storage)

    update_C(storage)


def harvest_loss(storage):
    """
    Description:
        Carbon loss during harvest
    """

    storage.C_harvest_gas = storage.C * storage.C_harvest_gas_percent

    storage.C_harvest_particle = storage.C * storage.C_harvest_particle_percent


def storage_loss(storage):
    """
    Description:
        Carbon loss during feed storage
    """

    storage.C_storage_gas = storage.C * storage.C_storage_gas_percent

    storage.C_storage_leachate = storage.C * storage.C_storage_leachate_percent


def feed_out_loss(storage):
    """
    Description:
        Carbon loss during feed out
    """

    storage.C_feed_out_gas = storage.C * storage.C_feed_out_gas_percent

    storage.C_feed_out_particle = storage.C * storage.C_feed_out_particle_percent


def update_C(storage):
    """
    Description:
        Update stored carbon based on calculated losses
    """

    storage.C_loss = (storage.C_harvest_gas + storage.C_harvest_particle +
                      storage.C_storage_gas + storage.C_storage_leachate +
                      storage.C_feed_out_gas + storage.C_feed_out_particle)

    storage.C -= storage.C_loss

    storage.DM -= storage.C_loss
