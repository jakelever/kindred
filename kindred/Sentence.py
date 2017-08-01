import kindred
import networkx as nx
import itertools
import sys
import six

class Sentence:
	"""
	Set of tokens for a sentence after parsing
	"""
	
	def __init__(self, tokens, dependencies, entitiesWithLocations, sourceFilename=None):
		"""
		Constructor for Sentence class
		
		:param tokens: List of tokens in sentence
		:param dependencies: List of dependencies from dependency path. Should be a list of tuples with form (tokenindex1,tokenindex2,dependency_type)
		:param entitiesWithLocations: List of entities associated with tokens. Should be a list of tuples with form (kindred.Entity, list of tokenindices)"
		:param sourceFilename: Filename of the source document
		:type tokens: list of kindred.Token
		:type dependencies: list of tuples
		:type entitiesWithLocations: list of tuples
		:type sourceFilename: str
		"""

		assert isinstance(tokens, list)
		for token in tokens:
			assert isinstance(token,kindred.Token)
		
		# Check that each entityWithLocation is a tuple of an entity with a location
		assert isinstance(entitiesWithLocations, list)
		for entityWithLocation in entitiesWithLocations:
			assert isinstance(entityWithLocation,tuple)
			assert len(entityWithLocation) == 2
			assert isinstance(entityWithLocation[0],kindred.Entity)
			assert isinstance(entityWithLocation[1],list)
			
		# Check the format of the Dependencies
		dependencyErrorMsg = "Each dependency is expected to be a tuple of (tokenindex1,tokenindex2,dependency_type). Token index can be -1 to indicate an incoming edge."
		assert isinstance(dependencies, list), dependencyErrorMsg
		for dependency in dependencies:
			assert isinstance(dependency,tuple),dependencyErrorMsg
			assert len(dependency) == 3,dependencyErrorMsg
			assert isinstance(dependency[0],int),dependencyErrorMsg
			assert isinstance(dependency[1],int),dependencyErrorMsg
			assert isinstance(dependency[2], six.string_types),dependencyErrorMsg
			assert dependency[0] >= -1 and dependency[0] < len(tokens), dependencyErrorMsg
			assert dependency[1] >= -1 and dependency[1] < len(tokens), dependencyErrorMsg
		
		self.tokens = tokens
		self.entitiesWithLocations = entitiesWithLocations
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		self.entityIDToType = { e.entityID:e.entityType for e,_ in self.entitiesWithLocations }
		self.entityIDToLoc = { e.entityID:loc for e,loc in self.entitiesWithLocations }

		self.candidateRelationsWithClasses = []
		self.candidateRelationsProcessed = False
	
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)
	
	def __repr__(self):
		return self.__str__()
	
	def addCandidateRelation(self, relation, relationtypeClass):
		"""
		Adds a candidate relation to a list of candidate relations associated with this sentence
		
		:param relation: Candidate relation to add to sentence
		:param relationtypeClass: Class index for type of candidate relation
		:type relation: kindred.Relation
		:type relationtypeClass: int
		"""

		self.candidateRelationsWithClasses.append((relation,relationtypeClass))

	def extractMinSubgraphContainingNodes(self, minSet):
		"""
		Find the minimum subgraph of the dependency graph that contains the provided set of nodes. Useful for finding dependency-path like structures
		
		:param minSet: List of token indices
		:type minSet: List of ints
		:return: All the nodes and edges in the minimal subgraph
		:rtype: Tuple of nodes,edges where nodes is a list of token indices, and edges are the associated dependency edges between those tokens
		"""

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

	def getEntityIDs(self):
		"""
		Get the list of entity IDs contained within this sentence
		
		:return: List of entity IDs
		:rtype: List of ints
		"""

		return [ e.entityID for e,_ in self.entitiesWithLocations ]
		
	def getEntityType(self,entityID):
		"""
		Get the entity type for a particular entity in this sentence given the entity ID
		
		:param entityID: Entity ID
		:type entityID: int
		:return: The entity type of the corresponding entity
		:rtype: str
		"""
		
		return self.entityIDToType[entityID]


