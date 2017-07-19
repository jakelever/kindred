
from collections import defaultdict
import itertools

import kindred

class CandidateBuilder:
	"""
	Generates set of all possible relations in corpus.
	"""
	def __init__(self):
		self.initialized = False
	
	def build(self,corpus):
		assert isinstance(corpus,kindred.Corpus)
			
		parser = kindred.Parser()
		parser.parse(corpus)
		
		if not self.initialized:
			self.relTypes = set()
		
			for doc in corpus.documents:
				knownRelations = doc.getRelations()
				for r in knownRelations:
					assert isinstance(r,kindred.Relation)
				for processedSentence in doc.processedSentences:
					tmpRelTypesAndArgCount = [ tuple([r.relationType] + r.argNames) for r in knownRelations ]
					self.relTypes.update(tmpRelTypesAndArgCount)
				
			self.relTypes = sorted(list(self.relTypes))
			self.relClasses = { relType:(i+1) for i,relType in enumerate(self.relTypes) }
			
			self.initialized = True
		
		candidateRelations = []
		candidateClasses = []
		
		for doc in corpus.documents:
			existingRelations = defaultdict(list)
			for r in doc.getRelations():
				assert isinstance(r,kindred.Relation)
				
				relationType = r.relationType
				entityIDs = tuple(r.entityIDs)
				
				relKey = tuple([r.relationType] + r.argNames)
				if relKey in self.relClasses:
					relationClass = self.relClasses[relKey]
					existingRelations[entityIDs].append(relationClass)

			for processedSentence in doc.processedSentences:
				entitiesInSentence = processedSentence.getEntityIDs()
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence,2):
					candidateRelation = kindred.Relation(entityIDs=list(entitiesInRelation))
					candidateClass = [0]
					relKey = tuple(entitiesInRelation)
					if relKey in existingRelations:
						candidateClass = existingRelations[relKey]
					
					candidateRelations.append(candidateRelation)
					candidateClasses.append(candidateClass)
					
		assert len(candidateRelations) == len(candidateClasses)
		
		return self.relTypes, candidateRelations, candidateClasses
