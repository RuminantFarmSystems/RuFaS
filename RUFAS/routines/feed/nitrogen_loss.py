"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_loss.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the nitrogen loss during harvest, storage, and feedout.
             The only function meant to be used outside of this file is the
             update_all() function. The other functions are meant to serve as
             helper functions within this file.

Feed attribute definitions:

Feed values updated by update_all():

"""
###############################################################################


def update_all(feed):
    CP_loss(feed)

    NPN_loss(feed)

    update_CP(feed)


def CP_loss(feed):
    feed.CP_gas = feed.crude_protein * feed.CP_gas_percent

    feed.CP_leachate = feed.crude_protein * feed.CP_leachate_percent


def NPN_loss(feed):
    feed.NPN += feed.crude_protein * feed.NPN_min_percent


def update_CP(feed):
    feed.crude_protein -= (feed.CP_gas + feed.CP_leachate)

    feed.dry_matter -= (feed.CP_gas + feed.CP_leachate)



