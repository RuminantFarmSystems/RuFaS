################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# ration.py - 
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import math

#------------------------------------------------------------------------------
# Class: Ration
# 
#------------------------------------------------------------------------------
class Ration():

	def __init__(self, data):
		pass

	def optimize_feed_ration(self):

		self.estimate_rqmts()
		self.estimate_protein_energy_rqmts()
		self.estimate_rumen_protein()
		self.setup_LP()

		#
		# RUN LINEAR PROGRAM
		#

	def estimate_rqmts(self):

		#
		# Inputs
		#
		pass

	def estimate_protein_energy_rqmts(self):
		pass

	def estimate_rumen_protein(self):
		pass

	def setup_LP():
		pass
