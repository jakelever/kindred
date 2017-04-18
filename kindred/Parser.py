
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
					
			parses = nltkutils.parseSentences(d.getText())
			
			for tokens,dependencies in parses:
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
					
				sentenceData = kindred.ParsedSentenceWithEntities(tokens, dependencies, entityLocs, entityTypes)
				allSentenceData.append(sentenceData)
		return allSentenceData
	
	#return allSentenceData