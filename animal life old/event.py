import random
import numpy as np

# life events for cows
class cowEvent(object):
	date = 0
	event = ''
	
	# Method: __init__
	''' 
		Description:
			initialize a cow life event
		Input: 
			date: the date counter for the cow (from birth)
			event: the event happened on that day
		Output:
			events of the cow's life
	'''
	def __init__(self, date, event):
		self.date = date
		self.event = event
