
import kindred

class CandidateGenerator:
	def __init__(self):
		pass
	
	def generate(self,trainData):
		assert isinstance(trainData,list)
		for t in trainData:
			assert isinstance(t,kindred.RelationData) or isinstance(t,kindred.TextAndEntityData)