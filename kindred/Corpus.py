import kindred

class Corpus:
	"""
	Collection of text documents.
	"""
	
	def __init__(self,text=None):
		"""
		Constructor
		
		:param self: Reference to object
		:param text: Optional SimpleTag text to initalize a single document
		:type self: kindred.Corpus
		:type text: String (with SimpleTag format XML)
		"""

		self.documents = []
		if not text is None:
			doc = kindred.Document(text)
			self.addDocument(doc)
		self.parsed = False

		self.relationTypes = None

	def addDocument(self,doc):
		"""
		Add a single document to the corpus
		
		:param self: Reference to object
		:param doc: Document to add
		:type self: kindred.Corpus
		:type doc: kindred.Document
		"""

		assert isinstance(doc,kindred.Document)
		self.documents.append(doc)


	def addRelationTypes(self,relationTypes):
		"""
		Add a set of relation types that have been identified in corpus
		
		:param self: Reference to object
		:param relationTypes: List of relation type names
		:type self: kindred.Corpus
		:type relationTypes: List of strings
		"""

		self.relationTypes = relationTypes

	def clone(self):
		"""
		Clone the corpus
		
		:param self: Reference to object
		:type self: kindred.Corpus
		:return: Clone of the corpus
		:rtype: kindred.Corpus
		"""

		cloned = Corpus()
		for doc in self.documents:
			cloned.addDocument(doc.clone())
		return cloned
	
	def getCandidateClasses(self):
		"""
		Get all the classes (i.e. indices of relation types) for all the candidate relations in this corpus.
		
		:param self: Reference to object
		:type self: kindred.Corpus
		:return: List of indices (corresponding to the relation types) for each candidate relation. 0 means no relation type
		:rtype: List of integers
		"""

		classes = []
		for doc in self.documents:
			classes += doc.getCandidateClasses()
		return classes
		
	def getCandidateRelations(self):
		"""
		Get all the candidate relations in this corpus.
		
		:param self: Reference to object
		:type self: kindred.Corpus
		:return: List of candidate relations
		:rtype: List of kindred.Relation
		"""

		relations = []
		for doc in self.documents:
			relations += doc.getCandidateRelations()
		return relations
		
	def getEntityMapping(self):
		"""
		:param self: Reference to object
		:type self: kindred.Corpus
		:return: return description
		:rtype: the return type description
		"""

		entityMapping = {}
		for doc in self.documents:
			for e in doc.entities:
				entityMapping[e.entityID] = e
		return entityMapping

	def getRelations(self):
		"""
		:param self: Reference to object
		:type self: kindred.Corpus
		:return: return description
		:rtype: the return type description
		"""

		relations = []
		for doc in self.documents:
			relations += doc.getRelations()
		return relations

	def removeRelations(self):
		"""
		:param self: Reference to object
		:type self: kindred.Corpus
		"""

		for doc in self.documents:
			doc.removeRelations()
