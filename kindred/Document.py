import kindred


class Document:
	"""
	Span of text with associated tagged entities and relations between entities.
	"""
	
	def __init__(self,text,entities=None,relations=None,sourceFilename=None,metadata={},loadFromSimpleTag=False):
		"""
		Constructor for a Document that can take text using the SimpleTag XML format, or a set of Entities and Relations with associated text.
		
		:param text: Text in document (plain-text, or SimpleTag)
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

		cloned = Document(self.text,entities=self.entities,relations=self.relations,sourceFilename=self.sourceFilename)
		return cloned

	def removeRelations(self):
		"""
		Remove all relations in this document
		"""
		self.relations = []

