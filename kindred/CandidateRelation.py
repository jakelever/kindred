import kindred

class CandidateRelation:
	def __init__(self,processedSentence,entitiesInRelation):
		assert isinstance(processedSentence,kindred.ProcessedSentence)
		assert isinstance(entitiesInRelation,tuple)
		assert len(entitiesInRelation) > 1
		
		entitiesInSentence = processedSentence.getEntityIDs()
		
		for entityID in entitiesInRelation:
			assert entityID in entitiesInSentence, "All entities in candidate relation should actually be in the associated sentence"
			
		self.processedSentence = processedSentence
		self.entitiesInRelation = entitiesInRelation
		
	def getEntityTypes(self):
		return [ self.processedSentence.getEntityType(eID) for eID in self.entitiesInRelation]

		
	def __str__(self):
		return str((self.processedSentence.__str__(),self.entitiesInRelation))
		
	def __repr__(self):
		return self.__str__()
		
