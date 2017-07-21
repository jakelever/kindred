import kindred

class Sentence:
	"""
	Set of tokens for a sentence after parsing
	"""
	
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)

	def getEntityIDs(self):
		return [ e.entityID for e,_ in self.entitiesWithLocations ]
		
	def getEntityType(self,entityID):
		return self.entityIDToType[entityID]

	def addCandidateRelation(self, relation, relationtypeClass):
		self.candidateRelationsWithClasses.append((relation,relationtypeClass))

	def __init__(self, tokens, dependencies, entitiesWithLocations, sourceFilename=None):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(entitiesWithLocations, list)
		for entityWithLocation in entitiesWithLocations:
			assert isinstance(entityWithLocation,tuple)
			assert len(entityWithLocation) == 2
			assert isinstance(entityWithLocation[0],kindred.Entity)
			assert isinstance(entityWithLocation[1],list)
		
		self.tokens = tokens
		self.entitiesWithLocations = entitiesWithLocations
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		self.entityIDToType = { e.entityID:e.entityType for e,_ in self.entitiesWithLocations }
		self.entityIDToLoc = { e.entityID:loc for e,loc in self.entitiesWithLocations }

		self.candidateRelationsWithClasses = []
		self.candidateRelationsProcessed = False
	

