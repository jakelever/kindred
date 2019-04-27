import kindred
from collections import OrderedDict

class Document:
	"""
	Span of text with associated tagged entities and relations between entities.

	:ivar text: Text in document (plain text or SimpleTag)
	:ivar entities: Entities in document
	:ivar relations: Relations in document
	:ivar sourceFilename: Filename that this document came from
	:ivar metadata: IDs and other information associated with the source (e.g. PMID)
	:ivar sentences: List of sentences (:class:`kindred.Sentence`) if the document has been parsed
	"""
	
	def __init__(self,text,entities=None,relations=None,sourceFilename=None,metadata={},loadFromSimpleTag=False):
		"""
		Constructor for a Document that can take text using the SimpleTag XML format, or a set of Entities and Relations with associated text.
		
		:param text: Text in document (plain text or SimpleTag)
		:param entities: Entities in document
		:param relations: Relations in document
		:param sourceFilename: Filename that this document came from
		:param metadata: IDs and other information associated with the source (e.g. PMID)
		:param loadFromSimpleTag: Assumes the text parameter is in the SimpleTag format and will extract entities and relations accordingly
		:type text: str
		:type entities: list of kindred.Entity
		:type relations: list of kindred.Relation
		:type sourceFilename: str
		:type metadata: dict
		:type loadFromSimpleTag: bool
		"""

		self.sourceFilename = sourceFilename
		self.metadata = metadata

		if loadFromSimpleTag:
			assert entities is None and relations is None, 'Entities and relations will be extracted from SimpleTag. They cannot also be passed in as parameters'

			docToCopy = kindred.loadFunctions.parseSimpleTag(text)
			assert isinstance(docToCopy,kindred.Document)
			self.text = docToCopy.text
			self.entities = docToCopy.entities
			self.relations = docToCopy.relations
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
		Add an entity to this document. If document has been parsed, it will add the entity into the sentence structure and associated with tokens.
		
		:param entity: Entity to add
		:type entity: kindred.Entity
		"""

		self.entities.append(entity)

		if self.sentences:
			for sentence in self.sentences:
				overlappingTokens = [ i for i,t in enumerate(sentence.tokens) if any (not (t.endPos <= eStart or t.startPos >= eEnd) for eStart,eEnd in entity.position ) ]
				if overlappingTokens:
					sentence.addEntityAnnotation(entity,overlappingTokens)

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

		cloned = Document(self.text,entities=self.entities,relations=self.relations,sourceFilename=self.sourceFilename)
		return cloned

	def removeEntities(self):
		"""
		Remove all entities in this document
		"""
		self.entities = []
	
	def removeRelations(self):
		"""
		Remove all relations in this document
		"""
		self.relations = []

	def splitIntoSentences(self):
		"""
		Create a new corpus with one document for each sentence in this document.

		:return: Corpus with one document per sentence
		:rtype: kindred.Corpus
		"""

		sentenceCorpus = kindred.Corpus()
		
		for sentence in self.sentences:
			sentenceStart = sentence.tokens[0].startPos
			
			entitiesInSentence = [ entity for entity,tokenIndices in sentence.entityAnnotations ]

			entityMap = OrderedDict()
			for e in entitiesInSentence:
				startPos,endPos = e.position[0]
				newPosition = [ (startPos-sentenceStart, endPos-sentenceStart) ]
				newE = kindred.Entity(e.entityType,e.text,newPosition,e.sourceEntityID,e.externalID)
				entityMap[e] = newE

			relationsInSentence = [ r for r in self.relations if all( e in entitiesInSentence for e in r.entities ) ]
			newRelationsInSentence = []
			for r in relationsInSentence:
				newEntitiesInRelation = [ entityMap[e] for e in r.entities ]
				newRelation = kindred.Relation(r.relationType,newEntitiesInRelation,r.argNames,r.probability)
				newRelationsInSentence.append(newRelation)

			newEntitiesInSentence = list(entityMap.values())
			doc = kindred.Document(sentence.text,newEntitiesInSentence,newRelationsInSentence)

			newTokens = [ kindred.Token(t.word,t.lemma,t.partofspeech,t.startPos-sentenceStart,t.endPos-sentenceStart) for t in sentence.tokens ]

			newSentence = kindred.Sentence(sentence.text,newTokens,sentence.dependencies,sentence.sourceFilename)
			newEntityAnnotations = [ (entityMap[e],tokenIndices) for e,tokenIndices in sentence.entityAnnotations ]
			newSentence.entityAnnotations = newEntityAnnotations
			doc.sentences = [newSentence]

			sentenceCorpus.addDocument(doc)

		return sentenceCorpus

		
