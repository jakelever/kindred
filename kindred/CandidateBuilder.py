
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
			existingRelationsAndArgNames = defaultdict(list)
			for r in doc.relations:
				assert isinstance(r,kindred.Relation)
				entities = tuple(r.entities)
				existingRelationsAndArgNames[entities].append((r.relationType,tuple(r.argNames)))

			for sentence in doc.sentences:
				entitiesInSentence = [ entity for entity,tokenIndices in sentence.entityAnnotations ]
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence, self.entityCount):
					typesInRelation = tuple([ e.entityType for e in entitiesInRelation ])
					if not self.acceptedEntityTypes is None and not typesInRelation in self.acceptedEntityTypes:
						# Relation doesn't contain the right entity types (so skip it)
						continue

					knownTypesAndArgNames = list(set(existingRelationsAndArgNames[entitiesInRelation]))
					knownTypesAndArgNames = [ (relationType,list(argNames)) for relationType,argNames in knownTypesAndArgNames ]
				
					candidateRelation = kindred.CandidateRelation(entities=list(entitiesInRelation),knownTypesAndArgNames=knownTypesAndArgNames,sentence=sentence)
					candidates.append(candidateRelation)

		return candidates

