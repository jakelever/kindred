
from collections import defaultdict
import itertools

import kindred

class CandidateBuilder:
	"""
	Generates set of all possible relations in corpus.
	"""
	def __init__(self,acceptedEntityPairs=None):
		"""
		Constructor

		:param acceptedEntityPairs: Pairs of entities that candidate relations must match. None will match all candidate relations.
		:type acceptedEntityPairs: list of tuples
		"""
		self.fitted = False

		assert acceptedEntityPairs is None or isinstance(acceptedEntityPairs,list)
		if acceptedEntityPairs is None:
			self.acceptedEntityPairs = None
		else:
			for acceptedEntityPair in acceptedEntityPairs:
				assert isinstance(acceptedEntityPair,tuple)
				assert len(acceptedEntityPair) == 2
			self.acceptedEntityPairs = set(acceptedEntityPairs)

	def fit_transform(self,corpus):
		"""
		Creates the set of all possible relations that exist within the given corpus and adds these to the corpus under each kindred.Sentence instance. Each relation will be contained within a single sentence. This fitting function should be called the first time in order to initialise the set of known relationship types.
		
		:param corpus: Corpus of text with which to build relation candidates
		:type corpus: kindred.Corpus
		"""

		assert self.fitted == False, "CandidateBuilder has already been fit to corpus"
		assert isinstance(corpus,kindred.Corpus)
		assert corpus.candidatesFound == False, "Candidates already exist in corpus."

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
		assert corpus.candidatesFound == False, "Candidates already exist in corpus."

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
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence,2):
					candidateRelation = kindred.Relation(entityIDs=list(entitiesInRelation))
					candidateClass = [0]
					relKey = tuple(entitiesInRelation)
					if relKey in existingRelations:
						candidateClass = existingRelations[relKey]

					includeCandidate = True
					if not self.acceptedEntityPairs is None:
						typesInRelation = tuple([ sentence.getEntityType(eID) for eID in entitiesInRelation ])
						includeCandidate = (typesInRelation in self.acceptedEntityPairs)

					if includeCandidate:
						sentence.addCandidateRelation(candidateRelation,candidateClass)

				sentence.candidateRelationsProcessed = True
					
		corpus.addRelationTypes(self.relTypes)
		corpus.candidatesFound = True

