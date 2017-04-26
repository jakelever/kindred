
from collections import defaultdict
import itertools

import kindred
from kindred.Parser_corenlp import Parser

class CandidateBuilder:
	def __init__(self):
		self.initialized = False
	
	def build(self,data):
		assert isinstance(data,list)
		for t in data:
			assert isinstance(t,kindred.RelationData) or isinstance(t,kindred.TextAndEntityData)
			
		parser = Parser()
		processedSentences = parser.parse(data)
		
		
		assert isinstance(processedSentences,list)
		for processedSentence in processedSentences:
			assert isinstance(processedSentence,kindred.ProcessedSentence)
		
		#entityIDsToEntityTypes = data.getEntityIDsToEntityTypes()
		
		if not self.initialized:
			self.relTypes = set()
		
			for processedSentence in processedSentences:
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
		
		for processedSentence in processedSentences:
			
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
