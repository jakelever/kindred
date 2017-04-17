
class RelationClassifier:
	"""
	This is a class. Fantastic!
	"""
	def __init__(self):
		"""
		Constructor-time
		"""
		pass

	def train(self,data):
		"""
		Does stuff
		"""
		assert isinstance(data,TextAndEntityData)

	def predict(self,data):
		if isinstance(data,string):
			processed_data = Utils.convert_tagged_text(data)
		else:
			processed_data = data

		assert isinstance(processed_data,TextAndEntityData)

		assert 1 == 0

