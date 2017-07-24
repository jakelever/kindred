import kindred
import networkx as nx
import itertools
import sys

class Sentence:
	"""
	Set of tokens for a sentence after parsing
	"""
	
	def extractMinSubgraphContainingNodes(self, minSet):
		assert isinstance(minSet, list)
		for i in minSet:
			assert isinstance(i, int)
			assert i >= 0
			assert i < len(self.tokens)
		G1 = nx.Graph()
		for a,b,depType in self.dependencies:
			G1.add_edge(a,b,dependencyType=depType)

		G2 = nx.Graph()
		paths = {}

		minSet = sorted(list(set(minSet)))
		setCount1 = len(minSet)
		minSet = [ a for a in minSet if G1.has_node(a) ]
		setCount2 = len(minSet)
		if setCount1 != setCount2:
			sys.stderr.write("WARNING. %d node(s) not found in dependency graph!\n" % (setCount1-setCount2))
		for a,b in itertools.combinations(minSet,2):
			try:
				path = nx.shortest_path(G1,a,b)
				paths[(a,b)] = path
				G2.add_edge(a,b,weight=len(path))
			except nx.exception.NetworkXNoPath:
				sys.stderr.write("WARNING. No path found between nodes %d and %d!\n" % (a,b))
			
		# TODO: This may through an error if G2 ends up having multiple components. Catch it gracefully.
		minTree = nx.minimum_spanning_tree(G2)
		nodes = set()
		allEdges = set()
		for a,b in minTree.edges():
			path = paths[(min(a,b),max(a,b))]
			for i in range(len(path)-1):
				a,b = path[i],path[i+1]
				dependencyType = G1.get_edge_data(a,b)['dependencyType']
				edge = (min(a,b),max(a,b),dependencyType)
				allEdges.add(edge)
			nodes.update(path)

		return nodes,allEdges
	
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)
	
	def __repr__(self):
		return self.__str__()

	def getEntityIDs(self):
		return [ e.entityID for e,_ in self.entitiesWithLocations ]
		
	def getEntityType(self,entityID):
		return self.entityIDToType[entityID]

	def addCandidateRelation(self, relation, relationtypeClass):
		self.candidateRelationsWithClasses.append((relation,relationtypeClass))

	def __init__(self, tokens, dependencies, entitiesWithLocations, sourceFilename=None):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(entitiesWithLocations, list)
		for entityWithLocation in entitiesWithLocations:
			assert isinstance(entityWithLocation,tuple)
			assert len(entityWithLocation) == 2
			assert isinstance(entityWithLocation[0],kindred.Entity)
			assert isinstance(entityWithLocation[1],list)
		
		self.tokens = tokens
		self.entitiesWithLocations = entitiesWithLocations
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		self.entityIDToType = { e.entityID:e.entityType for e,_ in self.entitiesWithLocations }
		self.entityIDToLoc = { e.entityID:loc for e,loc in self.entitiesWithLocations }

		self.candidateRelationsWithClasses = []
		self.candidateRelationsProcessed = False
	

