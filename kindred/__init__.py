
from kindred import *
import xml.etree.ElementTree
import sys

from kindred import CandidateBuilder


class Entity:
	nextInternalID = 1

	def __init__(self,entityType,text,pos,sourceEntityID=None):
		posErrorMsg = "Entity position must be list of tuples (startPos,endPos)"

		if sys.version_info >= (3, 0):
			assert isinstance(entityType,str)
			assert isinstance(text,str)
		else:
			assert isinstance(entityType,basestring) or isinstance(entityType,unicode)
			assert isinstance(text,basestring) or isinstance(text,unicode)

		assert isinstance(pos,list), posErrorMsg
		for p in pos:
			assert isinstance(p,tuple), posErrorMsg
			assert len(p) == 2, posErrorMsg
			assert isinstance(p[0],int), posErrorMsg
			assert isinstance(p[1],int), posErrorMsg
	
		self.entityType = entityType
		self.sourceEntityID = sourceEntityID
		self.text = text
		self.pos = pos
		
		self.entityID = Entity.nextInternalID
		Entity.nextInternalID += 1
		
	def __str__(self):
		out = "%s:'%s' id=%d %s" % (self.entityType,self.text,self.entityID,str(self.pos))
		return out
		
	def __repr__(self):
		return self.__str__()
		
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

class Relation:
	def __init__(self,relationType,entityIDs,argNames=None):
		assert isinstance(entityIDs,list)

		self.relationType = relationType
		self.entityIDs = entityIDs
		self.argNames = argNames
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

	def __str__(self):
		return "[Relation %s %s %s]" % (self.relationType,str(self.entityIDs),str(self.argNames))

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		if self.argNames is None:
			return hash((self.relationType,tuple(self.entityIDs)))
		else:
			return hash((self.relationType,tuple(self.entityIDs),tuple(self.argNames)))

class TextAndEntityData:
	def __init__(self,text,sourceFilename=None,entities=None):
		self.sourceFilename = sourceFilename

		if entities is None:
			self.text,self.entities = self.processTaggedText(text)
		else:
			self.text = text
			self.entities = entities
	

	def processTaggedText(self,text):

		text = text.replace('>','<')
		split = text.split('<')
		
		tagStyle = None
		isTag = False
		currentText = ""
		openTags = {}
		minID = 1
		
		preEntities = {}
		for section in split:
			if isTag:
				tagSplit = section.split(' ')
				assert len(tagSplit) == 1 or len(tagSplit) == 2
				if len(tagSplit) == 1:
					if section.startswith('/'): # close a tag
						entityType = section[1:]
						assert entityType in openTags, "Trying to close a non-existent %s element" % entityType
						
						entityStart,sourceEntityID = openTags[entityType]
						entityEnd = len(currentText)
						entityText = currentText[entityStart:]
						#entity = Entity(entityType,sourceEntityID,entityText,pos=[(entityStart,entityEnd)])
						#entities.append(entity)
						key = (sourceEntityID,entityType)
						if key in preEntities:
							preEntities[key]['text'] += ' ' + entityText
							preEntities[key]['pos'].append((entityStart,entityEnd))
						else:
							preEntities[key] = {}
							preEntities[key]['text'] = entityText
							preEntities[key]['pos'] = [(entityStart,entityEnd)]
						
						
						del openTags[entityType]
					else: # open a tag
						assert tagStyle != 2, "Cannot mix entity tags with and without IDs"
						tagStyle = 1
					
						entityType = section
						openTags[entityType] = (len(currentText),minID)
						minID += 1
				elif len(tagSplit) == 2:
					assert tagStyle != 1, "Cannot mix entity tags with and without IDs"
					tagStyle = 2
						
					entityType,idinfo = tagSplit
					assert idinfo.startswith('id=')
					idinfoSplit = idinfo.split('=')
					assert len(idinfoSplit) == 2
					sourceEntityID = int(idinfoSplit[1])
					
					openTags[entityType] = (len(currentText),sourceEntityID)
			else:
				currentText += section
				
			# Flip each iteration
			isTag = not isTag
			
		assert len(openTags) == 0, "All tags were not closed in %s" % text
		
		entities = []
		preEntitiesKeys = sorted(list(preEntities.keys()))
		for (sourceEntityID,entityType) in preEntitiesKeys:
			entityInfo = preEntities[(sourceEntityID,entityType)]
			entity = Entity(entityType,entityInfo['text'],entityInfo['pos'],sourceEntityID)
			entities.append(entity)
		
		return currentText,entities
		
	def getEntities(self):
		return self.entities
		
	def getSourceEntityIDsToEntityIDs(self):
		return {e.sourceEntityID:e.entityID for e in self.entities}
	
	def getEntityIDsToSourceEntityIDs(self):
		return {e.entityID:e.sourceEntityID for e in self.entities}
	
	def getEntityIDs(self):
		return [e.entityID for e in self.entities]

	def getSourceFilename(self):
		return self.sourceFilename
		
	def getText(self):
		return self.text
		
	def __str__(self):
		return str((self.text,self.entities.__str__()))
		
	def __repr__(self):
		return self.__str__()
		
class RelationData:
	def __init__(self,text,relationsWithSourceEntityIDs,sourceFilename=None,entities=None):
		assert isinstance(relationsWithSourceEntityIDs,list)
		for r in relationsWithSourceEntityIDs:
			assert isinstance(r,Relation)

		self.textAndEntityData = TextAndEntityData(text,sourceFilename=sourceFilename,entities=entities)
			
		sourceEntityIDsToEntityIDs = self.textAndEntityData.getSourceEntityIDsToEntityIDs()
		sourceEntityIDs = sourceEntityIDsToEntityIDs.keys()
			
		relations = []
		for r in relationsWithSourceEntityIDs:
			for e in r.entityIDs:
				assert e in sourceEntityIDs, "Entities in relation must occur in the associated text"
			relationEntityIDs = [ sourceEntityIDsToEntityIDs[e] for e in r.entityIDs ]
			newR = Relation(r.relationType,relationEntityIDs,r.argNames)
			relations.append(newR)
			
		self.relations = relations
		
	def getEntities(self):
		return self.textAndEntityData.getEntities()
		
	def getText(self):
		return self.textAndEntityData.getText()
		
	def getTextAndEntities(self):
		return self.textAndEntityData
		
	def getRelations(self):
		return self.relations
	
	def getSourceEntityIDsToEntityIDs(self):
		return self.textAndEntityData.getSourceEntityIDsToEntityIDs()
	
	def getEntityIDsToSourceEntityIDs(self):
		return self.textAndEntityData.getEntityIDsToSourceEntityIDs()
		
	def getEntityIDs(self):
		return self.textAndEntityData.getEntityIDs()

	def getSourceFilename(self):
		return self.textAndEntityData.getSourceFilename()

	def __str__(self):
		return str((self.textAndEntityData.__str__(),self.relations))
		
	def __repr__(self):
		return self.__str__()
	
class CandidateRelation:
	def __init__(self,processedSentence,entitiesInRelation):
		assert isinstance(processedSentence,ProcessedSentence)
		assert isinstance(entitiesInRelation,tuple)
		assert len(entitiesInRelation) > 1
		
		entitiesInSentence = processedSentence.getEntityIDs()
		
		for entityID in entitiesInRelation:
			assert entityID in entitiesInSentence, "All entities in candidate relation should actually be in the associated sentence"
			
		self.processedSentence = processedSentence
		self.entitiesInRelation = entitiesInRelation
		
	def __str__(self):
		return str((self.processedSentence.__str__(),self.entitiesInRelation))
		
	def __repr__(self):
		return self.__str__()
		
	
class Token:
	def __init__(self,word,lemma,partofspeech,startPos,endPos):
		self.word = word
		self.lemma = lemma
		self.partofspeech = partofspeech
		self.startPos = startPos
		self.endPos = endPos

	def __str__(self):
		return self.word
		
	def __repr__(self):
		return self.__str__()

class ProcessedEntity:
	def __init__(self,entityType,entityLocs,entityID,sourceEntityID):
		self.entityType = entityType
		self.entityLocs = entityLocs
		self.entityID = entityID
		self.sourceEntityID = sourceEntityID

	def __str__(self):
		return "[ProcessedEntity %s %s %s %s]" % (self.entityType,str(self.entityLocs),str(self.entityID),str(self.sourceEntityID))

	def __repr__(self):
		return self.__str__()
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

class ProcessedSentence:
	# TODO: Camelcase consistency in this class

	def printDependencyGraph(self):
		print("digraph sentence {")
		used = set()
		for a,b,_ in self.dependencies:
			used.update([a,b])
			aTxt = "ROOT" if a == -1 else str(a)
			bTxt = "ROOT" if b == -1 else str(b)

			print("%s -> %s;" % (aTxt,bTxt))

		for i,token in enumerate(self.tokens):
			if i in used:
				print("%d [label=\"%s\"];" % (i,token.word))
		print("}")
		
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)

	def getEdgeTypes(self,edges):
		types = [ t for a,b,t in self.dependencies if (a,b) in edges or (b,a) in edges ]
		return types

	def extractSubgraphToRoot(self,minSet):
		neighbours = defaultdict(list)
		for a,b,_ in self.dependencies:
			neighbours[b].append(a)
			
		toProcess = list(minSet)
		alreadyProcessed = []
		edges = []
		while len(toProcess) > 0:
			thisOne = toProcess[0]
			toProcess = toProcess[1:]
			alreadyProcessed.append(thisOne)
			for a in neighbours[thisOne]:
				if not a in alreadyProcessed:
					toProcess.append(a)
					edges.append((a,thisOne))
		return alreadyProcessed,edges
		
	def extractMinSubgraphContainingNodes(self, minSet):
		import networkx as nx
		
		assert isinstance(minSet, list)
		for i in minSet:
			assert isinstance(i, int)
			assert i >= 0
			assert i < len(self.tokens)
		G1 = nx.Graph()
		for a,b,_ in self.dependencies:
			G1.add_edge(a,b)

		G2 = nx.Graph()
		paths = {}

		minSet = sorted(list(set(minSet)))
		setCount1 = len(minSet)
		minSet = [ a for a in minSet if G1.has_node(a) ]
		setCount2 = len(minSet)
		if setCount1 != setCount2:
			print("WARNING. %d node(s) not found in dependency graph!" % (setCount1-setCount2))
		for a,b in itertools.combinations(minSet,2):
			try:
				path = nx.shortest_path(G1,a,b)
				paths[(a,b)] = path
				G2.add_edge(a,b,weight=len(path))
			except nx.exception.NetworkXNoPath:
				print("WARNING. No path found between nodes %d and %d!" % (a,b))
			
		# TODO: This may throw an error if G2 ends up having multiple components. Catch it gracefully.
		minTree = nx.minimum_spanning_tree(G2)
		nodes = set()
		allEdges = set()
		for a,b in minTree.edges():
			path = paths[(min(a,b),max(a,b))]
			for i in range(len(path)-1):
				a,b = path[i],path[i+1]
				edge = (min(a,b),max(a,b))
				allEdges.add(edge)
			nodes.update(path)

		return nodes,allEdges
	
	def buildDependencyInfo(self):
		self.dep_neighbours = defaultdict(set)
		for (a,b,type) in self.dependencies:
			self.dep_neighbours[a].add(b)
			self.dep_neighbours[b].add(a)
		self.dep_neighbours2 = defaultdict(set)
		for i in self.dep_neighbours:
			for j in self.dep_neighbours[i]:
				self.dep_neighbours2[i].update(self.dep_neighbours[j])
			self.dep_neighbours2[i].discard(i)
			for j in self.dep_neighbours[i]:
				self.dep_neighbours2[i].discard(j)
		
	def invertTriggers(self):
		self.locsToTriggerIDs = {}
		self.locsToTriggerTypes = {}
		for triggerid,locs in self.entityLocs.items():
			type = self.entityTypes[triggerid]
			self.locsToTriggerIDs[tuple(locs)] = triggerid
			self.locsToTriggerTypes[tuple(locs)] = type

	def getEntityIDs(self):
		return [ e.entityID for e in self.processedEntities ]
		
	def getEntityType(self,entityID):
		return self.entityIDToType[entityID]

	def __init__(self, tokens, dependencies, processedEntities, relations=[], sourceFilename=None):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(processedEntities, list)
		for e in processedEntities:
			assert isinstance(e,ProcessedEntity)
		
		self.tokens = tokens
		self.processedEntities = processedEntities
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		entitiesInSentence = self.getEntityIDs()
		for r in relations:
			assert isinstance(r,Relation)
			for relationEntityID in r.entityIDs:
				assert relationEntityID in entitiesInSentence, "Relation cannot contain entity not in this sentence"

		self.entityIDToType = { e.entityID:e.entityType for e in self.processedEntities }
		
		self.relations = relations
	
		#self.invertTriggers()

