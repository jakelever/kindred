import kindred


class Document:
	def __init__(self,text,entities=None,relations=None,relationsUseSourceIDs=True,sourceFilename=None):
		loadFromSimpleTag = (entities is None)

		self.sourceFilename = sourceFilename

		if loadFromSimpleTag:
			dataToCopy = kindred.loadFunctions.parseSimpleTag(text)
			self.text = dataToCopy.getText()
			self.entities = dataToCopy.getEntities()
			self.relations = dataToCopy.getRelations()
		else:
			self.text = text
			
			assert isinstance(entities,list)
			for e in entities:
				assert isinstance(e,kindred.Entity)
			self.entities = entities
			
			if relations is None:
				self.relations = []
			else:
				assert isinstance(relations,list)
				for r in relations:
					assert isinstance(r,kindred.Relation)
				self.relations = relations

		# We'll need to translate source IDs to internal IDs
		if relationsUseSourceIDs and not loadFromSimpleTag:
			sourceEntityIDsToEntityIDs = self.getSourceEntityIDsToEntityIDs()
			sourceEntityIDs = sourceEntityIDsToEntityIDs.keys()
			correctedRelations = []
			for r in self.relations:
				for e in r.entityIDs:
					assert e in sourceEntityIDs, "Entities in relation must occur in the associated text. %s does not" % e
				relationEntityIDs = [ sourceEntityIDsToEntityIDs[e] for e in r.entityIDs ]
				correctedR = kindred.Relation(r.relationType,relationEntityIDs,r.argNames)
				correctedRelations.append(correctedR)
				
			self.relations = correctedRelations

		self.processedSentences = []

	def clone(self):
		cloned = Document(self.text,entities=self.entities,relations=self.relations,relationsUseSourceIDs=False,sourceFilename=self.sourceFilename)
		return cloned

	def removeRelations(self):
		self.relations = []

	def addProcessedSentence(self,sentence):
		assert isinstance(sentence,kindred.ProcessedSentence)
		self.processedSentences.append(sentence)
	
	def addRelation(self,relation):
		self.relations.append(relation)

	def getEntities(self):
		return self.entities
		
	def getText(self):
		return self.text
		
	def getRelations(self):
		return self.relations
	
	def getSourceEntityIDsToEntityIDs(self):
		return {e.sourceEntityID:e.entityID for e in self.entities}
	
	def getEntityIDsToSourceEntityIDs(self):
		return {e.entityID:e.sourceEntityID for e in self.entities}
		
	def getEntityIDsToEntityTypes(self):
		return {e.entityID:e.entityType for e in self.entities}
	
	def getEntityIDsToEntities(self):
		return {e.entityID:e for e in self.entities}
	
	def getEntityIDs(self):
		return [e.entityID for e in self.entities]

	def getSourceFilename(self):
		return self.sourceFilename

	def __str__(self):
		return str((self.textAndEntityData.__str__(),self.relations))
		
	def __repr__(self):
		return self.__str__()
	

