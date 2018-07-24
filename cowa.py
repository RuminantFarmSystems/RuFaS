from event import cowEvent
import random
import numpy as np

# initial a cow with ID
class Cow(object):
	ID = 0

	global next_id
	def next_id(self):
		Cow.ID = Cow.ID + 1
		return Cow.ID
	
	# Method: __init__
	''' 
		Description:
			initialize common parameters for all cows
		Input: 
			mean: mean of new birth weight 
			stv: standard diviation of birth weight
			cow_type: breed of the cow
			date: the date of the simulation when the calf was born
			days_born: age of the animal
		Output:
			daily animal stutas 
	'''
	def __init__(self, mean, stv, cow_type, date, days_born=0):
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
	''' 
		Description:
			Check if the cow is sold (male calves will be sold)
		Input: 
			Sex ratio of the selected semen type
		Output:
			True/False value indicating if sold
	'''   
	def sold(self):
		return self.sex == 'M'

	# Method: is_culled
	''' 
		Description:
			Check if the the cow is culled
		Input: 
			From involuentury and voluentury culling section
		Output:
			True/False value inidicating if culled
	'''
	def is_culled(self):
		return self.culled
		
	# Method: is_preg
	''' 
		Description:
			Check if the the cow is pregnant
		Input: 
			Pregnant check results
		Output:
			True/False value indicating pregnancy
	'''
	def is_preg(self):
		if (self.preg_days == -12):
			return False
		else:
			return True

	# Method: is_milk
	''' 
		Description:
			Check if the the cow is in milk
		Input: 
			Check last calving and dry/cull events
		Output:
			True/False value indicating if milking
	'''
	def is_milk(self):
		if (self.days_in_milk == -1):
			return False
		else:
			return True

	# Method: update
	''' 
		Description:
			update common daily information for each cow
		Input: 
			weight_increase: average daily gain
		Output:
			manure: production 
			feed: comsumption 
	'''
	def update(self, weight_increase):
		feed = self.weight * 0.03
		manure = 0.06 * self.weight

		self.days_born = self.days_born + 1 
		self.weight = self.weight + weight_increase

		return manure, feed