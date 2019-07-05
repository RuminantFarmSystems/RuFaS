'''
RUFAS: Ruminant Farm Systems Model
File name: animal_events.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file initialize life events with the age of the animal
				when event happens and the description of the event.
'''
###############################################################################

import random
import numpy as np

# life events for cows
class AnimalEvents(object):	
	# Method: __init__
	def __init__(self):
		self.events = {}

	'''
		Description:
			add a cow life event
		Input:
			date: the date counter for the cow (from birth)
			description: the event happened on that day
		Output:
	'''
	def add_event(self, date, description):
		if date in self.events:
			self.events[date].append(description)
		else:
			self.events[date] = [description]

	def __str__(self):
		res_str = ''
		for key, value in sorted(self.events.items()):
			res_str += '\tDays born {}: {} \n'.format(key, value)

		return res_str