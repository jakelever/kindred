import kindred


class ProcessedSentence:
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)

	def getEntityIDs(self):
		return [ e.entityID for e in self.processedEntities ]
		
	def getEntityType(self,entityID):
		return self.entityIDToType[entityID]

	def __init__(self, tokens, dependencies, processedEntities, sourceFilename=None):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(processedEntities, list)
		for e in processedEntities:
			assert isinstance(e,kindred.ProcessedEntity)
		
		self.tokens = tokens
		self.processedEntities = processedEntities
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		self.entityIDToType = { e.entityID:e.entityType for e in self.processedEntities }
	

