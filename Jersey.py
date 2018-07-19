from __future__ import print_function
from cowa import Cow
import numpy as np
import random
import math
import matplotlib.pyplot as plt

class Jersey(Cow):
	# estrus_method: ED or TAI or ED-TAI
	def __init__(self, estrus_method, date):
		self.estrus_method = estrus_method

		self.cull_stat = []
		self.calving_stat = []
		self.milk_produced_stat = []
		self.milk_produced_total = [0, 0, 0] # p1, p2, p3+
		self.milk_produced_days = [0, 0, 0] # p1, p2, p3+
		self.service_stat = []
		self.manure_stat = []
		self.feed_stat = []
		self.estrus_stat = []
		# self.heat_detected_dates = []

		# lactarion curve parameters
		self.a = [24.5, 30.9, 33.6]
		self.b = [18.3, 15.1, 17.9]
		self.c = [-2.9, -2.0, -2.2]
		self.d = [0.00089, 0.00173, 0.00198]

		# ED
		if (estrus_method == 'ed'):
			self.vwp = 60
			self.conception_rate = 0.35
		elif (estrus_method == 'ed_tai'):
			# ED-TAI
			self.vwp = 50
			self.conception_rate = 0.40
		else:
			# TAI, not yet implemented
			self.conception_rate = 0.290

		Cow.__init__(self, 27.2, 0.58, 'J', date)

	def update(self, date):
		give_ai = False
		calving = False
		milk_produced = 0
		cull = False

		if not (self.days_in_milk == -1):
			self.days_in_milk = self.days_in_milk + 1

		if (self.num_birth == 0) and (self.days_born > 780):
			cull = True

		weight_increase = 0
		season = date % 90 % 4
		mean_weight_inc = 0.84
		if season == 1:
			mean_weight_inc = 0.82
		elif season == 2:
			mean_weight_inc = 0.8
		elif season == 3:
			mean_weight_inc = 0.77

		if self.days_born <= 70:
			weight_increase = np.random.normal(0.46, 0.02)
		elif self.weight < 408 :
			weight_increase = np.random.normal(0.54, 0.02)

		manure, feed = Cow.update(self, weight_increase)

		# determine the next estrus date
		# print(str(self.num_birth) + " " + str(self.first_estrus) + " " + str(self.next_estrus_date) + " " + str(self.preg_days))
		if ((self.days_born > 360 and self.num_birth == 0) or ((not self.num_birth == 0) and (not self.first_estrus))) and (self.next_estrus_date == -1):
			self.next_estrus_date = np.trunc(np.random.normal(21, 2.5)) + self.days_born
		elif (self.first_estrus) and (self.next_estrus_date == -1):
			self.next_estrus_date = np.trunc(np.random.normal(19, 11)) + self.days_born

		if (not self.next_estrus_date == -1) and (not (self.next_estrus_date + self.birthday) in self.estrus_stat):
			self.estrus_stat.append(self.next_estrus_date + self.birthday)

		# Heat detection
		# print(str(self.days_born) + " " + str(self.next_estrus_date) + " " + str(Cow.is_preg(self)))
		if (self.days_born == self.next_estrus_date) and (not Cow.is_preg(self)):
			if (self.days_in_milk > self.vwp and self.days_in_milk <= 356) or (self.days_in_milk == -1):
				rand = random.random()
				if (rand <= 0.6):
					self.preg_days = -2
					self.expected_due = np.trunc(np.random.normal(278,6))	
					# self.heat_detected_dates.append(date)
				else:
					self.next_estrus_date = -1
					if (not self.num_birth == 0):
						self.first_estrus = False	# first_estrus was set to true after first birth
			else:
				self.next_estrus_date = -1
				if (not self.num_birth == 0):
					self.first_estrus = False

		if (self.days_in_milk > 356):
			# Cow is culled
			cull = True

		if (Cow.is_preg(self)):
			self.preg_days = self.preg_days + 1
			# on the 0th day, give AI
			if (self.preg_days == 0):
				give_ai = True
				self.service_stat.append(date)
			
			# on the 32nd day, preg diagnosis #1
			if (self.preg_days == 32):
				rand = random.random()
				if (rand > self.conception_rate):
					# conception failed
					self.preg_days = -12
					self.next_estrus_date = -1
					if (not self.num_birth == 0):
						self.first_estrus = False
					if (self.estrus_method == 'ed'):
						self.conception_rate = self.conception_rate - 0.026

			# on the 91st day, preg diagnosis #2
			if (self.preg_days == 91):
				rand = random.random()
				if (rand <= 0.096):
				 	# abortion
				 	self.preg_days = -12
					self.next_estrus_date = -1
					if (not self.num_birth == 0):
						self.first_estrus = False
					if (self.estrus_method == 'ed'):
						self.conception_rate = self.conception_rate - 0.026

			# on the 200th day, preg diagnosis #3
			if (self.preg_days == 200):
				rand = random.random()
				if (rand <= 0.017):
				 	# abortion
				 	self.preg_days = -12
					self.next_estrus_date = -1
					if (not self.num_birth == 0):
						self.first_estrus = False
					if (self.estrus_method == 'ed'):
						self.conception_rate = self.conception_rate - 0.026

			# dry
			if (self.preg_days == 220):
				self.days_in_milk = -1

			if (self.preg_days == self.expected_due):
				calving = True
				self.first_estrus = True
				self.days_in_milk = 0
				self.preg_days = -12
				self.next_estrus_date = -1
				self.num_birth = self.num_birth + 1
				if (self.estrus_method == 'ed'):
					self.conception_rate = 0.339
				# stillbirth
				rand = random.random()
				if (rand <= 0.065):
					calving = False

		if (Cow.is_milk(self)):
			i = min(self.num_birth-1, 2)
			milk_produced = self.a[i] * (1 - math.exp((self.c[i]-self.days_in_milk) / self.b[i]) / 2) * math.exp((0 - self.d[i]) * self.days_in_milk)
			if (self.num_birth == 1):
				self.milk_produced_total[0] = self.milk_produced_total[0] + milk_produced
			elif (self.num_birth == 2):
				self.milk_produced_total[1] = self.milk_produced_total[1] + milk_produced
			else:
				self.milk_produced_total[2] = self.milk_produced_total[2] + milk_produced

		if (self.num_birth == 1):
			self.milk_produced_days[0] = self.milk_produced_days[0] + 1
		elif (self.num_birth == 2):
			self.milk_produced_days[1] = self.milk_produced_days[1] + 1
		elif (self.num_birth > 2):
			self.milk_produced_days[2] = self.milk_produced_days[2] + 1

		# stats
		if cull:
			self.cull_stat.append(date)
			self.culled = True
		if calving:
			self.calving_stat.append(date)
		self.milk_produced_stat.append(milk_produced)
		self.manure_stat.append(manure)
		self.feed_stat.append(feed)

		return cull, calving, milk_produced, give_ai, manure, feed

	def print_stat(self):
		print('Date born: ', end='')
		print(self.birthday, end='')
		print('\n')

		print('Estrus dates: ', end='')
		for i in xrange(0, len(self.estrus_stat)): print(self.estrus_stat[i], end=' ')
		print('\n')

		# print('Heat detection dates: ', end='')
		# for i in xrange(0, len(self.heat_detected_dates)): print(self.heat_detected_dates[i], end=' ')
		# print('\n')

		print('Service dates: ', end='')
		for i in xrange(0, len(self.service_stat)): print(self.service_stat[i], end=' ')
		print('\n')

		print('Calving dates: ', end='')
		for i in xrange(0, len(self.calving_stat)): print(self.calving_stat[i], end=' ')
		print('\n')

		if (len(self.cull_stat) > 0):
			print('Culled on: ' + str(self.cull_stat[0]), end='')
		print('\n')

		print('milk production p1 per year: ', end='')
		if (self.milk_produced_total[0] == 0):
			print('N/A', end='')
		else:
			print(self.milk_produced_total[0]/self.milk_produced_days[0]*356, end='')
		print('\n')

		print('milk production p2 per year: ', end='')
		if (self.milk_produced_total[1] == 0):
			print('N/A', end='')
		else:
			print(self.milk_produced_total[1]/self.milk_produced_days[1]*356, end='')
		print('\n')

		print('milk production p3+ per year: ', end='')
		if (self.milk_produced_total[2] == 0):
			print('N/A', end='')
		else:
			print(self.milk_produced_total[2]/self.milk_produced_days[2]*356, end='')
		print('\n')

		plt.figure('Cow ' + str(self.id) + ' milk production')
		plt.plot(self.milk_produced_stat)
		plt.show()

	def get_stat(self):
		return self.milk_produced_total, self.milk_produced_days