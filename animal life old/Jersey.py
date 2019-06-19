from cowa import Cow
import numpy as np

# Class for Jersey. Temporarily disabled
class Jersey(Cow):
	# Method: __init__
	''' 
		Description:
			initialize Jersey
		Input: 
			repro_method:
		Output:
	'''
	def __init__(self, repro_method):
		Cow.__init__(self, 27.2, 0.58, repro_method, 'J')

	# Method: update
	''' 
		Description:
			updates Jersey's information for each day. Simutes any events happened to the Jersey each day
		Input: 
			feed_price: price of the feed
			date: the date counter for the entire farm
		Output:
			manure:
			feed:
	'''
	def update(self, feed_price, date):
		weight_increase = 0
		if self.days_born <= 70:
			weight_increase = np.random.normal(0.46, 0.02)
		elif self.weight < 408 :
			weight_increase = np.random.normal(0.54, 0.02)

		return Cow.update(self, weight_increase, feed_price)
