
class RelationClassifier:
	def __init__(self):
		pass

	def train(self,data):
		assert isinstance(data,TextAndEntityData)

	def predict(self,data):
		if isinstance(data,string):
			processed_data = Utils.convert_tagged_text(data)
		else:
			processed_data = data

		assert isinstance(processed_data,TextAndEntityData)

		assert 1 == 0

