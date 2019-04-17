import random
import numpy as np

# life events for cows
class AnimalEvents(object):	
	# Method: __init__
	''' 
		Description:
			initialize a cow life event
		Input: 
			date: the date counter for the cow (from birth)
			event: the event happened on that day
		Output:
	'''
	def __init__(self):
		self.events = {}

	def add_event(self,date, description):
		if date in self.events:
			self.events[date].append(description)
		else:
			self.events[date] = [description]

	def __str__(self):
		res_str = ''
		for key, value in sorted(self.events.items()):
			res_str += '\tDays born {}: {} \n'.format(key, value)

		return res_str