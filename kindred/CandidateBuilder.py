
from collections import defaultdict
import itertools

import kindred

class CandidateBuilder:
	"""
	Generates set of all possible relations in corpus.
	"""
	def __init__(self):
		self.fitted = False

	def fit_transform(self,corpus):
		assert self.fitted == False, "CandidateBuilder has already been fit to corpus"
		assert isinstance(corpus,kindred.Corpus)

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
	
		return self.transform(corpus)

	def transform(self,corpus):
		assert self.fitted == True, "CandidateBuilder must be fit to corpus first"
		assert isinstance(corpus,kindred.Corpus)

		if not corpus.parsed:
			parser = kindred.Parser()
			parser.parse(corpus)

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

			for sentence in doc.sentences:
				entitiesInSentence = sentence.getEntityIDs()
							
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

