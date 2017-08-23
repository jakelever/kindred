import kindred
import random

class Corpus:
	"""
	Collection of text documents.
	"""
	
	def __init__(self,text=None):
		"""
		Constructor
		
		:param text: Optional SimpleTag text to initalize a single document
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
		
		:param doc: Document to add
		:type doc: kindred.Document
		"""

		assert isinstance(doc,kindred.Document)
		self.documents.append(doc)


	def addRelationTypes(self,relationTypes):
		"""
		Add a set of relation types that have been identified in corpus
		
		:param relationTypes: List of relation type names
		:type relationTypes: List of strings
		"""

		self.relationTypes = relationTypes

	def clone(self):
		"""
		Clone the corpus
		
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
		
		:return: List of candidate relations
		:rtype: List of kindred.Relation
		"""

		relations = []
		for doc in self.documents:
			relations += doc.getCandidateRelations()
		return relations
		
	def getEntityMapping(self):
		"""
		Gets mapping from entity ID to entity instances
		
		:return: Map of entity ID to entity instance
		:rtype: dict
		"""

		entityMapping = {}
		for doc in self.documents:
			for e in doc.entities:
				entityMapping[e.entityID] = e
		return entityMapping

	def getRelations(self):
		"""
		Get all relations in this corpus
		
		:return: List of relations
		:rtype: list
		"""

		relations = []
		for doc in self.documents:
			relations += doc.getRelations()
		return relations

	def removeRelations(self):
		"""
		Remove all relations in this corpus
		"""

		for doc in self.documents:
			doc.removeRelations()

