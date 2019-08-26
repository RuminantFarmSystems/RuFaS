"""
RUFAS: Ruminant Farm Systems Model

File name: protein_degradation.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating
             protein degradation during harvest, storage, and feedout.
             The only function meant to be used outside of this file is the
             update_all() function. The other functions are meant to serve as
             helper functions within this file.

Feed attribute definitions:

Feed values updated by update_all():

"""
###############################################################################


def update_all(feed):
    degrade_protein(feed)


def degrade_protein(feed):
    pass
