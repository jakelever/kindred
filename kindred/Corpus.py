import kindred

class Corpus:
	"""
	Collection of text documents.
	"""
	
	def __init__(self,text=None):
		self.documents = []
		if not text is None:
			doc = kindred.Document(text)
			self.addDocument(doc)

	def addDocument(self,doc):
		assert isinstance(doc,kindred.Document)
		self.documents.append(doc)

	def clone(self):
		cloned = Corpus()
		for doc in self.documents:
			cloned.addDocument(doc.clone())
		return cloned

	def getRelations(self):
		relations = []
		for doc in self.documents:
			relations += doc.getRelations()
		return relations
		
	def getEntityMapping(self):
		entityMapping = {}
		for doc in self.documents:
			for e in doc.entities:
				entityMapping[e.entityID] = e
		return entityMapping

	def removeRelations(self):
		for doc in self.documents:
			doc.removeRelations()
