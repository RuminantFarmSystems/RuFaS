"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_loss.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the carbon loss during harvest, storage, and feedout.
             The only function meant to be used outside of this file is the
             update_all() function. The other functions are meant to serve as
             helper functions within this file.

Feed attribute definitions:

Feed values updated by update_all():

"""


def update_all(feed):
    """
    Description:
        The only external function call. Runs the carbon loss sub-module
    """

    harvest_loss(feed)

    storage_loss(feed)

    feedout_loss(feed)

    update_carbon(feed)


def harvest_loss(feed):
    """
    Description:
        Carbon loss during harvest
    """

    feed.C_harvest_gas = feed.carbon * feed.C_harvest_gas_percent

    feed.C_harvest_particle = feed.carbon * feed.C_harvest_particle_percent


def storage_loss(feed):
    """
    Description:
        Carbon loss during feed storage
    """

    feed.C_storage_gas = feed.carbon * feed.C_storage_gas_percent

    feed.C_storage_leachate = feed.carbon * feed.C_storage_leachate_percent


def feedout_loss(feed):
    """
    Description:
        Carbon loss during feedout
    """

    feed.C_feedout_gas = feed.carbon * feed.C_feedout_gas_percent

    feed.C_feedout_particle = feed.carbon * feed.C_feedout_particle_percent


def update_carbon(feed):
    """
    Description:
        Update feed carbon based on calculated losses
    """

    carbon_loss = (feed.C_harvest_gas + feed.C_harvest_particle +
                   feed.C_storage_gas + feed.C_storage_leachate +
                   feed.C_feedout_gas + feed.C_feedout_particle)

    feed.carbon -= carbon_loss

    feed.dry_matter -= carbon_loss
