import random
import numpy as np

# life events for cows
class cowEvent(object):
	date = 0
	event = ''

	# Method: __init__
	def __init__(self, date, event):
		"""
		Initialize a cow life event

		Args:
			date: the date counter for the cow (from birth)
			event: string that represents the event happened on that day
		"""
		self.date = date
		self.event = event
