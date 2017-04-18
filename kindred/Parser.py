
import kindred
from intervaltree import Interval, IntervalTree
from collections import defaultdict
from kindred import nltkutils

class Parser:
	def __init__(self):
		pass
		
	def parse(self,data):
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.RelationData) or isinstance(d,kindred.TextAndEntityData)
			
		allSentenceData = []
		for d in data:
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.pos:
					denotationTree[a:b] = e.entityID
					
			sentences = nltkutils.parseSentences(d.getText())
			
			for tokens,dependencies in sentences:
				entityLocations = defaultdict(list)
				for i,t in enumerate(tokens):
					entities = denotationTree[t.startPos:t.endPos]
					for interval in entities:
						entityID = interval.data
						entityLocations[entityID].append(i)
					
				# Let's gather up the information about the "known" entities in the sentence
				entityLocs, entityTypes = {},{}
				for entityID,locs in entityLocations.iteritems():
					entityType = entityTypeLookup[entityID]
					entityLocs[entityID] = locs
					entityTypes[entityID] = entityType
					
				relations = []
				# Let's also put in the relation information if we can get it
				if isinstance(d,kindred.RelationData):
					tmpRelations = d.getRelations()
					entitiesInSentence = entityLocs.keys()
					for tmpRelation in tmpRelations:
						relationType = tmpRelation[0]
						relationEntityIDs = tmpRelation[1:]
						matched = [ (relationEntityID in entitiesInSentence) for relationEntityID in relationEntityIDs ]
						if all(matched):
							relations.append(tmpRelation)
					
				sentenceData = kindred.ProcessedSentence(tokens, dependencies, entityLocs, entityTypes, relations)
				allSentenceData.append(sentenceData)
		return allSentenceData
	
	#return allSentenceData