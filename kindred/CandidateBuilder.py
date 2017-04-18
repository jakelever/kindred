
from collections import defaultdict
import itertools

import kindred
from kindred.Parser import Parser

class CandidateBuilder:
	def __init__(self):
		pass
	
	def build(self,data):
		assert isinstance(data,list)
		for t in data:
			assert isinstance(t,kindred.RelationData) or isinstance(t,kindred.TextAndEntityData)
			
		parser = Parser()
		processedSentences = parser.parse(data)
		
		assert isinstance(processedSentences,list)
		for processedSentence in processedSentences:
			assert isinstance(processedSentence,kindred.ProcessedSentence)
		
		candidateRelations = []
		candidateClasses = []
		relTypes = set()
		
		for processedSentence in processedSentences:
			knownRelations = processedSentence.relations
			tmpRelTypes = [ (r[0],len(r)-1) for r in knownRelations ]
			relTypes.update(tmpRelTypes)
			
		relTypes = sorted(list(relTypes))
		relClasses = { relType:(i+1) for i,relType in enumerate(relTypes) }
		
		# Find the "cardinality" of relations (e.g. different number of arguments)
		narys = [ nary for _,nary in relTypes ]
		narys = sorted(list(set(narys)))
		
		for processedSentence in processedSentences:
			
			existingRelations = defaultdict(list)
			for r in processedSentence.relations:
				relationName = r[0]
				entityIDs = tuple(r[1:])
				relationClass = relClasses[(relationName,len(entityIDs))]
				existingRelations[entityIDs].append(relationClass)

			entitiesInSentence = processedSentence.getEntityIDs()
						
			for nary in narys:
				for entitiesInRelation in itertools.permutations(entitiesInSentence,nary):
					candidateRelation = kindred.CandidateRelation(processedSentence, entitiesInRelation)
					candidateClass = 0
					relKey = tuple(entitiesInRelation)
					if relKey in existingRelations:
						candidateClass = existingRelations[relKey]
					
					candidateRelations.append(candidateRelation)
					candidateClasses.append(candidateClass)
					
		assert len(candidateRelations) == len(candidateClasses)
		
		return relTypes, candidateRelations, candidateClasses