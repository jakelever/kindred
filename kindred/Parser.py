
import kindred
from intervaltree import Interval, IntervalTree
from collections import defaultdict
from kindred import nltkutils

class Parser:
	def __init__(self,depparser='stanford'):
		assert depparser == 'stanford' or depparser == 'malt'
		self.depparser = depparser

	def parse(self,data):
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.RelationData) or isinstance(d,kindred.TextAndEntityData)
			
		allSentenceData = []
		for d in data:
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					denotationTree[a:b] = e.entityID
					
			sentences = nltkutils.parseSentences(d.getText(),self.depparser)
			
			for tokens,dependencies in sentences:
				entityIDsToTokenLocs = defaultdict(list)
				for i,t in enumerate(tokens):
					entitiesOverlappingWithToken = denotationTree[t.startPos:t.endPos]
					for interval in entitiesOverlappingWithToken:
						entityID = interval.data
						entityIDsToTokenLocs[entityID].append(i)
					
				# Let's gather up the information about the "known" entities in the sentence
				processedEntities = []
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					entityType = entityTypeLookup[entityID]
					e = entityIDsToEntities[entityID]
					processedEntity = kindred.ProcessedEntity(e.entityType,entityLocs,entityID,e.sourceEntityID,e.position,e.text)
					processedEntities.append(processedEntity)
					
				relations = []
				# Let's also put in the relation information if we can get it
				if isinstance(d,kindred.RelationData):
					tmpRelations = d.getRelations()
					entitiesInSentence = entityIDsToTokenLocs.keys()
					for tmpRelation in tmpRelations:
						matched = [ (relationEntityID in entitiesInSentence) for relationEntityID in tmpRelation.entityIDs ]
						if all(matched):
							relations.append(tmpRelation)
					
				sentenceData = kindred.ProcessedSentence(tokens, dependencies, processedEntities, relations, d.getSourceFilename())
				allSentenceData.append(sentenceData)
		return allSentenceData
	
	#return allSentenceData
