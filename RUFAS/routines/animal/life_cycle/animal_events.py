"""
RUFAS: Ruminant Farm Systems Model
File name: animal_events.py
Author(s): Manfei Li, mli497@wisc.edu
			Militsa Sotirova, militsasotirova@gmail.com
Description: This file initialize life events with the age of the animal
				when event happens and the description of the event.
"""
###############################################################################

import copy


class AnimalEvents(object):
	def __init__(self):
		"""
		Initialization of AnimalEvents object.
		"""
		self.events = {}

	def init_from_string(self, events_str):
		"""
		Initialize event from a string

		Args:
			events_str: string representation of events
		"""
		split_by_date = list(filter(lambda x : x != '', list(
			map(lambda x: x.strip(), events_str.lower().split('days born ')))))

		for day in split_by_date:
			split = day.split(': ')
			date = int(split[0])
			events = list(filter(lambda x: (x != '[' and x != ']' and x != ', '), split[1].split('\'')))
			for event in events:
				self.add_event(date, event)

	def add_event(self, date, description):
		"""
		Add a cow life event

		Args:
			date: the date counter for the cow (from birth)
			description: the event happened on that day
		"""
		if date in self.events:
			self.events[date].append(description)
		else:
			self.events[date] = [description]

	def __str__(self):
		res_str = ''
		for key, value in sorted(self.events.items()):
			res_str += '\tdays born {}: {} \n'.format(key, value)

		return res_str
	
	def get_most_recent_date(self, event_description):
		"""
		Returns the most recent age at which the @event_description happened
		"""
		dates = copy.deepcopy(list(self.events.keys()))
		dates.reverse()
		for date in dates:
			if event_description in self.events[date]:
				return date
		return -1
