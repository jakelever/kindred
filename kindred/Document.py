import kindred


class Document:
	"""
	Span of text with associated tagged entities and relations between entities.
	"""
	
	def __init__(self,text,entities=None,relations=None,relationsUseSourceIDs=True,sourceFilename=None,metadata={},loadFromSimpleTag=False):
		"""
		Constructor for a Document that can take text using the SimpleTag XML format, or a set of Entities and Relations with associated text.
		
		:param text: Text in document (plain-text, or SimpleTag)
		:param entities: Entities in document
		:param relations: Relations in document
		:param relationsUseSourceIDs: description
		:param sourceFilename: description
		:param metadata: IDs and other information associated with the source (e.g. PMID)
		:param loadFromSimpleTag: Assumes the text parameter is in the SimpleTag format and will extract entities and relations accordingly
		:type text: type description
		:type entities: type description
		:type relations: type description
		:type relationsUseSourceIDs: type description
		:type sourceFilename: type description
		:type metadata: dict
		:type loadFromSimpleTag: bool
		"""

		self.sourceFilename = sourceFilename
		self.metadata = metadata

		if loadFromSimpleTag:
			assert entities is None and relations is None, 'Entities and relations will be extracted from SimpleTag. They cannot also be passed in as parameters'

			dataToCopy = kindred.loadFunctions.parseSimpleTag(text)
			self.text = dataToCopy.getText()
			self.entities = dataToCopy.getEntities()
			self.relations = dataToCopy.getRelations()
		else:
			self.text = text
			
			if entities is None:
				self.entities = []
			else:
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

		self.sentences = []
		
	def __repr__(self):
		"""
		String representation of Document
		
		:return: string representation
		:rtype: str
		"""
		return self.__str__()
	
	def __str__(self):
		"""
		String representation of Document
		
		:return: string representation
		:rtype: str
		"""

		return u"<Document %s %s %s>"  % (self.text,str(self.entities),str(self.relations))
	
	def addEntity(self,entity):
		"""
		Add an entity to this document
		
		:param entity: Entity to add
		:type entity: kindred.Entity
		"""

		self.entities.append(entity)

	def addRelation(self,relation):
		"""
		Add a relation to this document
		
		:param relation: Relation to add
		:type relation: kindred.Relation
		"""

		self.relations.append(relation)

	def addSentence(self,sentence):
		"""
		Add a sentence to this document
		
		:param sentence: Sentence to add
		:type sentence: kindred.Sentence
		"""

		assert isinstance(sentence,kindred.Sentence)
		self.sentences.append(sentence)
		
	def clone(self):
		"""
		Clones the document
		
		:return: Clone of the document
		:rtype: kindred.Document
		"""

		cloned = Document(self.text,entities=self.entities,relations=self.relations,relationsUseSourceIDs=False,sourceFilename=self.sourceFilename)
		return cloned

	def getCandidateClasses(self,entityCount):
		"""
		Get all the classes (i.e. indices of relation types) for all the candidate relations (of a given n-ary) in this document.
		
		:param entityCount: Number of entities (n-ary) in candidate relations
		:type entityCount: int
		:return: List of indices (corresponding to the relation types) for each candidate relation. 0 means no relation type
		:rtype: List of integers
		"""

		assert not self.sentences is None, "Document must be parsed and CandidateBuilder use to get candidate relations first"
		classes = []
		for sentence in self.sentences:
			assert entityCount in sentence.candidateRelationsEntityCounts, "CandidateBuilder use to get candidate relations first"
			classes += [ relationtypeClass for relation,relationtypeClass in sentence.candidateRelationsWithClasses[entityCount] ]
		return classes
	
	def getCandidateRelations(self,entityCount):
		"""
		Get all the candidate relations (of a given n-ary) in this corpus.
		
		:param entityCount: Number of entities (n-ary) in candidate relations
		:type entityCount: int
		:return: List of candidate relations
		:rtype: List of kindred.Relation
		"""

		assert not self.sentences is None, "Document must be parsed and CandidateBuilder use to get candidate relations first"
		relations = []
		for sentence in self.sentences:
			assert entityCount in sentence.candidateRelationsEntityCounts, "CandidateBuilder use to get candidate relations first"
			relations += [ relation for relation,relationtypeClass in sentence.candidateRelationsWithClasses[entityCount] ]
		return relations
		
	def getEntities(self):
		"""
		Get the entities for this document
		
		:return: List of entities
		:rtype: list of kindred.Entity
		"""
		
		return self.entities
	
	def getEntityIDs(self):
		"""
		Get the entity IDs for the entities in this document
		
		:return: List of entity IDs
		:rtype: list of int
		"""

		return [e.entityID for e in self.entities]
	
	def getEntityIDsToEntities(self):
		"""
		Get a mapping of entity IDs to entities
		
		:return: Map of entity ID to entity instance
		:rtype: dict
		"""

		return {e.entityID:e for e in self.entities}
		
	def getEntityIDsToEntityTypes(self):
		"""
		Get a mapping of entity IDs to entity types
		
		:return: Map of entity ID to entity types
		:rtype: dict
		"""

		return {e.entityID:e.entityType for e in self.entities}

	def getEntityIDsToSourceEntityIDs(self):
		"""
		Get a mapping of entity IDs to source entity IDs
		
		:return: Map of entity ID to source entity IDs
		:rtype: dict
		"""
		
		return {e.entityID:e.sourceEntityID for e in self.entities}
		
	def getRelations(self):
		"""
		Get the relations associated with the document
		
		:return: list of relations
		:rtype: list of kindred.Relation
		"""
		
		return self.relations
		
	def getSourceEntityIDsToEntityIDs(self):
		"""
		Get a mapping of source entity IDs to entity IDs
		
		:return: Map of source entity IDs to entity ID
		:rtype: dict
		"""
		
		return {e.sourceEntityID:e.entityID for e in self.entities}
		
	def getSourceFilename(self):
		"""
		Get the source filename for the document
		
		:return: Source filename
		:rtype: str
		"""
		
		return self.sourceFilename

	def getText(self):
		"""
		Get the text associated with the document
		
		:return: list of text
		:rtype: str
		"""
		
		return self.text

	def removeRelations(self):
		"""
		Remove all relations in this corpus
		"""
		self.relations = []

