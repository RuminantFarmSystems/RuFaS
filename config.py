import json

class Config():
	def __init__(self):
		with open('config.json', 'r') as f:
			self._config = json.load(f)

	def __getitem__(self, key):
		return self._config[key]

	def __getattr__(self, key):
		try:
			return self._config[key]
		except KeyError as e:
			raise AttributeError(e)
