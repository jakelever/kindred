
from collections import defaultdict
import itertools

import kindred
from kindred.Parser import Parser

class CandidateBuilder:
	def __init__(self):
		self.initialized = False
	
	def build(self,corpus):
		assert isinstance(corpus,kindred.Corpus)
			
		parser = Parser()
		parser.parse(corpus)
		
		if not self.initialized:
			self.relTypes = set()
		
			for doc in corpus.documents:
				for processedSentence in doc.processedSentences:
					knownRelations = processedSentence.relations
					for r in knownRelations:
						assert isinstance(r,kindred.Relation)
					
					tmpRelTypesAndArgCount = [ tuple([r.relationType] + r.argNames) for r in knownRelations ]
					self.relTypes.update(tmpRelTypesAndArgCount)
				
			self.relTypes = sorted(list(self.relTypes))
			self.relClasses = { relType:(i+1) for i,relType in enumerate(self.relTypes) }
			
			self.initialized = True
		
		candidateRelations = []
		candidateClasses = []
		
		for doc in corpus.documents:
			for processedSentence in doc.processedSentences:
				
				existingRelations = defaultdict(list)
				for r in processedSentence.relations:
					assert isinstance(r,kindred.Relation)
					
					relationType = r.relationType
					entityIDs = tuple(r.entityIDs)
					
					relKey = tuple([r.relationType] + r.argNames)
					if relKey in self.relClasses:
						relationClass = self.relClasses[relKey]
						existingRelations[entityIDs].append(relationClass)

				entitiesInSentence = processedSentence.getEntityIDs()
							
				for entitiesInRelation in itertools.permutations(entitiesInSentence,2):
					candidateRelation = kindred.CandidateRelation(processedSentence, entitiesInRelation)
					candidateClass = [0]
					relKey = tuple(entitiesInRelation)
					if relKey in existingRelations:
						candidateClass = existingRelations[relKey]
					
					candidateRelations.append(candidateRelation)
					candidateClasses.append(candidateClass)
					
		assert len(candidateRelations) == len(candidateClasses)
		
		return self.relTypes, candidateRelations, candidateClasses
