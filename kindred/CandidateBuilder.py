
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

	def build(self,corpus):
		"""
		Creates the set of all possible relations that exist within the given corpus. Each relation will be contained within a single sentence.
		
		:param corpus: Corpus of text with which to build relation candidates
		:type corpus: kindred.Corpus
		:return: List of candidate relations matching entityCount and acceptedEntityTypes
		:rtype: List of kindred.Relation
		"""
		assert isinstance(corpus,kindred.Corpus)
		assert corpus.parsed, "Corpus must have already been parsed"

		candidates = []
		for doc in corpus.documents:
			existingRelationsAndArgNames = defaultdict(lambda : (None,None))
			for r in doc.getRelations():
				assert isinstance(r,kindred.Relation)
				entityIDs = tuple(r.entityIDs)
				existingRelationsAndArgNames[entityIDs] = (r.relationType,r.argNames)

			for sentence in doc.sentences:
				entitiesInSentence = [ entity for entity,tokenIndices in sentence.entityAnnotations ]
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence, self.entityCount):
					entityIDsInRelation = tuple([ e.entityID for e in entitiesInRelation ])
					relationType,argNames = existingRelationsAndArgNames[entityIDsInRelation] # Is None if relation doesn't exist
					candidateRelation = kindred.Relation(relationType=relationType,entityIDs=list(entityIDsInRelation),argNames=argNames,sentence=sentence)

					includeCandidate = True
					if not self.acceptedEntityTypes is None:
						typesInRelation = tuple([ e.entityType for e in entitiesInRelation ])
						includeCandidate = (typesInRelation in self.acceptedEntityTypes)

					if includeCandidate:
						candidates.append(candidateRelation)

		return candidates

