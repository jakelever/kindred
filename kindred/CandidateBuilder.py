
from collections import defaultdict
import itertools

import kindred

class CandidateBuilder:
	"""
	Generates set of all possible relations in corpus.
	"""
	def __init__(self,entityCount=2,acceptedEntityTypes=None):
		"""
		Constructor

		:param entityCount: Number of entities in each relation (default=2)
		:param acceptedEntityTypes: Tuples of entities that candidate relations must match. Each entity should be the same length as entityCount. None will match all candidate relations.
		:type entityCount: int
		:type acceptedEntityTypes: list of tuples
		"""
		self.fitted = False

		assert isinstance(entityCount,int)
		assert entityCount >= 2
		self.entityCount = entityCount

		assert acceptedEntityTypes is None or isinstance(acceptedEntityTypes,list)
		if acceptedEntityTypes is None:
			self.acceptedEntityTypes = None
		else:
			for acceptedEntityType in acceptedEntityTypes:
				assert isinstance(acceptedEntityType,tuple)
				assert len(acceptedEntityType) == entityCount
			self.acceptedEntityTypes = set(acceptedEntityTypes)

	def fit_transform(self,corpus):
		"""
		Creates the set of all possible relations that exist within the given corpus and adds these to the corpus under each kindred.Sentence instance. Each relation will be contained within a single sentence. This fitting function should be called the first time in order to initialise the set of known relationship types.
		
		:param corpus: Corpus of text with which to build relation candidates
		:type corpus: kindred.Corpus
		"""

		assert self.fitted == False, "CandidateBuilder has already been fit to corpus"
		assert isinstance(corpus,kindred.Corpus)
		assert not self.entityCount in corpus.candidateRelationsEntityCounts, "Candidates for relations with entityCount=%d already exist in corpus." % self.entityCount

		if not corpus.parsed:
			parser = kindred.Parser()
			parser.parse(corpus)
		
		self.relTypes = set()
	
		for doc in corpus.documents:
			knownRelations = doc.getRelations()
			for r in knownRelations:
				assert isinstance(r,kindred.Relation)
			
			tmpRelTypesAndArgCount = [ tuple([r.relationType] + r.argNames) for r in knownRelations ]
			self.relTypes.update(tmpRelTypesAndArgCount)
			
		self.relTypes = sorted(list(self.relTypes))
		self.relClasses = { relType:(i+1) for i,relType in enumerate(self.relTypes) }
			
		self.fitted = True
	
		self.transform(corpus)

	def transform(self,corpus):
		"""
		Creates the set of all possible relations that exist within the given corpus and adds these to the corpus under each kindred.Sentence instance. Each relation will be contained within a single sentence.
		
		:param corpus: Corpus of text with which to build relation candidates
		:type corpus: kindred.Corpus
		"""
		assert self.fitted == True, "CandidateBuilder must be fit to corpus first"
		assert isinstance(corpus,kindred.Corpus)
		assert not self.entityCount in corpus.candidateRelationsEntityCounts, "Candidates for relations with entityCount=%d already exist in corpus." % self.entityCount

		if not corpus.parsed:
			parser = kindred.Parser()
			parser.parse(corpus)

		for doc in corpus.documents:
			existingRelations = defaultdict(list)
			for r in doc.getRelations():
				assert isinstance(r,kindred.Relation)
				
				entityIDs = tuple(r.entityIDs)
				
				relKey = tuple([r.relationType] + r.argNames)
				if relKey in self.relClasses:
					relationClass = self.relClasses[relKey]
					existingRelations[entityIDs].append(relationClass)

			for sentence in doc.sentences:
				entitiesInSentence = sentence.getEntityIDs()
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence, self.entityCount):
					candidateRelation = kindred.Relation(entityIDs=list(entitiesInRelation))
					candidateClass = [0]
					relKey = tuple(entitiesInRelation)
					if relKey in existingRelations:
						candidateClass = existingRelations[relKey]

					includeCandidate = True
					if not self.acceptedEntityTypes is None:
						typesInRelation = tuple([ sentence.getEntityType(eID) for eID in entitiesInRelation ])
						includeCandidate = (typesInRelation in self.acceptedEntityTypes)

					if includeCandidate:
						sentence.addCandidateRelation(candidateRelation,candidateClass)

				sentence.candidateRelationsEntityCounts.add(self.entityCount)
					
		corpus.addRelationTypes(self.relTypes)
		corpus.candidateRelationsEntityCounts.add(self.entityCount)

