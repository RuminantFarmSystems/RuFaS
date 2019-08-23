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

def update_all():
    CP_loss()

    NPN_loss()

def CP_loss():
    pass

def NPN_loss():
    pass
