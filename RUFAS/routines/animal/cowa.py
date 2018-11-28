from RUFAS.routines.animal.event import cowEvent
import random
import numpy as np

# initial a cow with ID
class Cow(object):
	'''
	A Cow object with a unique identification number and the characteristics
	of the cow's life.
	'''
	ID = 0

	global next_id
	def next_id(self):
		Cow.ID = Cow.ID + 1
		return Cow.ID

	# Method: __init__
	def __init__(self, mean, stv, cow_type, date, days_born=0):
	'''
	Initializes common parameters for all cows
	Args:
		mean: mean of new birth weight
		stv: standard diviation of birth weight
		cow_type: breed of the cow
		date: the date of the simulation when the calf was born
		days_born: age of the animal
	'''
		self.weight = np.random.normal(mean, stv)
		self.days_born = days_born
		self.type = cow_type
		self.birthday = date
		self.culled = False
		self.events = []

		self.events.append(cowEvent(0, 'born'))
		# Determine the sex of the cow
		sex_rand = random.random()
		if sex_rand < 0.1:
			self.sex = 'M'
		else:
			self.sex = 'F'

		if  self.sex == 'F':
			self.id = next_id(self)
			self.preg_days = -12
			self.concept_days = -1
			self.days_in_milk = -1
			self.next_estrus_date = -1
			self.num_birth = 0	 # num of cattles born
			self.first_estrus = False   # First estrus after calving

	# Method: sold
	def sold(self):
	'''
	Checks if the cow is sold (male calves will be sold)

	Returns
		True/False value indicating if sold
	'''
		return self.sex == 'M'

	# Method: is_culled
	def is_culled(self):
	'''
	Check if the the cow is culled

	Returns:
		True/False value inidicating if culled
	'''
		return self.culled

	# Method: is_preg
	def is_preg(self):
	'''
	Checks if the the cow is pregnant

	Returns:
		True/False value indicating pregnancy
	'''
		if (self.preg_days == -12):
			return False
		else:
			return True

	# Method: is_milk
	def is_milk(self):
	'''
	Checks if the the cow is in milk

	Returns:
		True/False value indicating if milking
	'''
		if (self.days_in_milk == -1):
			return False
		else:
			return True

	# Method: update
	def update(self, weight_increase):
	'''
	Updates common daily information for each cow

	Args:
		weight_increase: number for average daily gain

	Returns:
		manure: number for the daily production of manure
		feed: number for the daily consumption of feed
	'''
		feed = self.weight * 0.03
		manure = 0.06 * self.weight

		self.days_born = self.days_born + 1
		self.weight = self.weight + weight_increase

		return manure, feed
