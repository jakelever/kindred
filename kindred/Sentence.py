import kindred
import networkx as nx
import itertools
import sys
import six
from collections import defaultdict

class Sentence:
	"""
	Set of tokens for a sentence after parsing
	"""
	
	def __init__(self, text, tokens, dependencies, sourceFilename=None):
		"""
		Constructor for Sentence class
	
		:param text: Text of the sentence
		:param tokens: List of tokens in sentence
		:param dependencies: List of dependencies from dependency path. Should be a list of tuples with form (tokenindex1,tokenindex2,dependency_type)
		:param sourceFilename: Filename of the source document
		:type text: str
		:type tokens: list of kindred.Token
		:type dependencies: list of tuples
		:type sourceFilename: str
		"""

		assert isinstance(text, six.string_types)

		assert isinstance(tokens, list)
		for token in tokens:
			assert isinstance(token,kindred.Token)
		
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
		
		self.text = text
		self.tokens = tokens
		self.dependencies = dependencies
		self.sourceFilename = sourceFilename
		
		self.entityAnnotations = []
		
	def addEntityAnnotation(self, entity, tokenIndices):
		"""
		Add an entity annotation to this sentence. Associated a specific entity with the indices of specific tokens
		
		:param entity: Entity to add to sentence
		:param tokenIndices: List of token indices
		:type entity: kindred.Entity
		:type tokenIndices: List of ints
		"""
		
		assert isinstance(entity, kindred.Entity)
		assert isinstance(tokenIndices,list)
		for l in tokenIndices:
			assert l >= 0 and l < len(self.tokens), "Entity location must be an index of one of the tokens"
		self.entityAnnotations.append( (entity,tokenIndices) )
	
	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)
	
	def __repr__(self):
		return self.__str__()
	
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

