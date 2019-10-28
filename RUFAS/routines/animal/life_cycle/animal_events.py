'''
RUFAS: Ruminant Farm Systems Model
File name: animal_events.py
Author(s): Manfei Li, mli497@wisc.edu
		   Militsa Sotirova, militsasotirova@gmail.com
Description: This file initialize life events with the age of the animal
				when event happens and the description of the event.
'''
###############################################################################

import random
import numpy as np
import copy

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
	
	def get_most_recent_date(self, event_description):
		'''
		Returns the most recent age at which the @event_description happened
		'''
		dates = copy.deepcopy(list(self.events.keys()))
		dates.reverse()
		for date in dates:
			if event_description in self.events[date]:
				return date
		return -1