import kindred
import random

class Corpus:
	"""
	Collection of text documents.
	"""
	
	def __init__(self,text=None,loadFromSimpleTag=False):
		"""
		Constructor
		
		:param text: Optional SimpleTag text to initalize a single document
		:param loadFromSimpleTag: If text is provided, whether the text parameter is in the SimpleTag format and will extract entities and relations accordingly
		:type text: String (with SimpleTag format XML)
		:type loadFromSimpleTag: bool
		"""

		self.documents = []
		if not text is None:
			doc = kindred.Document(text,loadFromSimpleTag=loadFromSimpleTag)
			self.addDocument(doc)

		self.parsed = False

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
			relations += doc.relations
		return relations

	def removeRelations(self):
		"""
		Remove all relations in this corpus
		"""

		for doc in self.documents:
			doc.removeRelations()

	def split(self,trainFraction):
		"""
		Randomly split the corpus into two corpus for use as a training and test set

		:param trainFraction: Fraction of documents to use in training set
		:type trainFraction: float
		:return: Tuple of training and test corpus
		:rtype: (kindred.Corpus,kindred.Corpus)
		"""
		assert isinstance(trainFraction,float)
		assert trainFraction > 0.0 and trainFraction < 1.0
		trainIndices = random.sample(range(len(self.documents)),int(round(trainFraction*len(self.documents))))
		trainIndices = set(trainIndices)

		trainCorpus,testCorpus = kindred.Corpus(),kindred.Corpus()
		for i,doc in enumerate(self.documents):
			if i in trainIndices:
				trainCorpus.addDocument(doc)
			else:
				testCorpus.addDocument(doc)

		return trainCorpus,testCorpus

	def nfold_split(self,folds):
		"""
		Method for splitting up the corpus multiple times and is used for an n-fold cross validation approach (as a generator). Each iteration, the training and test set for that fold are provided.

		:param folds: Number of folds to create
		:type folds: int
		:return: Tuple of training and test corpus (for iterations=folds)
		:rtype: (kindred.Corpus,kindred.Corpus)
		"""
		assert isinstance(folds,int)
		assert folds > 0

		indices = list(range(len(self.documents)))
		random.shuffle(indices)

		chunkSize = int(len(self.documents)/float(folds))
		indexChunks = [ indices[i:i+chunkSize] for i in range(0,len(self.documents),chunkSize) ]

		for f in range(folds):
			trainCorpus,testCorpus = kindred.Corpus(),kindred.Corpus()
			for i,indexChunk in enumerate(indexChunks):
				for j in indexChunk:
					if i==f:
						testCorpus.addDocument(self.documents[j])
					else:
						trainCorpus.addDocument(self.documents[j])
			yield trainCorpus,testCorpus

