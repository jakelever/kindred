import sys
from collections import defaultdict, Counter, OrderedDict
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import coo_matrix, csr_matrix, lil_matrix, hstack, vstack
from sklearn.linear_model import LogisticRegression
from sklearn import neighbors
import numpy as np
import os
import itertools

import kindred

class SentenceModel:
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
			
		# TODO: This may through an error if G2 ends up having multiple components. Catch it gracefully.
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
		for triggerid,locs in self.predictedEntityLocs.items():
			type = self.predictedEntityTypes[triggerid]
			self.locsToTriggerIDs[tuple(locs)] = triggerid
			self.locsToTriggerTypes[tuple(locs)] = type
		for triggerid,locs in self.knownEntityLocs.items():
			type = self.knownEntityTypes[triggerid]
			self.locsToTriggerIDs[tuple(locs)] = triggerid
			self.locsToTriggerTypes[tuple(locs)] = type
	
	def __init__(self, tokens, dependencies, eventTriggerLocs, eventTriggerTypes, argumentTriggerLocs, argumentTriggerTypes):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(eventTriggerLocs, dict) 
		assert isinstance(eventTriggerTypes, dict)
		assert isinstance(argumentTriggerLocs, dict) 
		assert isinstance(argumentTriggerTypes, dict)
		
		assert len(eventTriggerLocs) == len(eventTriggerTypes)
		assert len(argumentTriggerLocs) == len(argumentTriggerTypes)
		
		self.tokens = tokens
		self.predictedEntityLocs = eventTriggerLocs
		self.predictedEntityTypes = eventTriggerTypes
		self.knownEntityLocs = argumentTriggerLocs
		self.knownEntityTypes = argumentTriggerTypes
		self.dependencies = dependencies
	
		self.invertTriggers()

class Example:
	def __str__(self):
		allSentenceIDs = sorted(list(set([ sentenceid for sentenceid,_ in self.arguments ])))
		tmpTokens = {}
		for sentenceid in allSentenceIDs:
			tmpTokens[sentenceid] = [ t.word for t in self.sentences[sentenceid].tokens ]
		for i,(sentenceid,locs) in enumerate(self.arguments):
			argname = "arg%d" % (i+1)
			for loc in locs:
				tmpTokens[sentenceid][loc] = "<%s>%s</%s>" % (argname,tmpTokens[sentenceid][loc],argname)
		sentenceTxts = [ " ".join(tmpTokens[sentenceid]) for sentenceid in allSentenceIDs ]
		txt = " . ".join(sentenceTxts)
		if isinstance(txt, unicode):
			return txt.encode('utf8')
		else:
			return txt
		
	def __init__(self, filename, sentences, arg_locs):
		#assert arg2 is None
		assert isinstance(filename, str) or isinstance(filename, unicode)
		assert isinstance(sentences, list)
		for sentence in sentences:
			assert isinstance(sentence, SentenceModel)
		
		self.filename = filename
		self.sentences = sentences
		#self.arg1_sentenceid = arg1_sentenceid
		#self.arg1_locs = arg1_locs
		#self.arguments = [(arg1_sentenceid, arg1_locs),(arg2_sentenceid, arg2_locs)]
		self.arguments = [ (0,loc) for loc in arg_locs ]

def SentenceToVerseSentence(s):
	assert isinstance(s,kindred.Sentence)
	argTypes = { e.entityID:e.entityType for e,locs in s.entitiesWithLocations }
	argLocs = { e.entityID:locs for e,locs in s.entitiesWithLocations }
	#def __init__(self, tokens, dependencies, eventTriggerLocs, eventTriggerTypes, argumentTriggerLocs, argumentTriggerTypes):

	verseS = SentenceModel(s.tokens,s.dependencies,{},{},argLocs,argTypes)

	return verseS

def findSentenceContainingRelation(corpus,r):
	for doc in corpus.documents:
		for sentence in doc.sentences:
			sentenceEntityIDs = sentence.getEntityIDs()
			relEntitiesInSentence = [ eID in sentenceEntityIDs for eID in r.entityIDs ]
			if all(relEntitiesInSentence):
				return sentence
	return None

def CandidateRelationToExample(corpus,r):
	assert isinstance(corpus,kindred.Corpus)
	assert isinstance(r,kindred.Relation)

	kindredSentence = findSentenceContainingRelation(corpus,r)

	eID_to_locs = { e.entityID:locs for e,locs in kindredSentence.entitiesWithLocations }
	verseSentence = SentenceToVerseSentence(kindredSentence)
	locs = [ eID_to_locs[eID] for eID in r.entityIDs ]
	example = Example("None",[verseSentence],locs)

	return example
			
class VERSEVectorizer:
	# Feature list
	# - ngrams for selected tokens
	# - ngrams for all tokens
	# - bigrams for all tokens
	# - ngrams for all tokens with POS
	# - ngrams for selected tokens with POS (or just POS?)
	# - bigrams on path from tokens to root
	
	"""
	Legacy code from VERSE that turns set of candidate relations into sparse matrix.
	"""
	
	def getFeatureNames(self):
		return self.vectorize(corpus=None,candidates=[],featureNamesOnly=True)
	
	def vectorize(self,corpus,candidates,featureNamesOnly=False):
		examples = [ CandidateRelationToExample(corpus,c) for c in candidates ]

		if featureNamesOnly == False:
			assert len(examples) > 0, "Expected more than zero examples to vectorize"
			for e in examples:
				assert self.argCount == len(e.arguments), 'All examples must have the same number of arguments (%d)' % self.argCount
			
		data = OrderedDict()
		if "ngrams_betweenEntities" in self.chosenFeatures:
			data["ngrams_betweenEntities"] = self.doNgramsBetweenEntities(examples,featureNamesOnly)
		
		#"dependencyPathNearSelected"
		if "dependencyPathNearSelected" in self.chosenFeatures:
			for i in range(self.argCount):
				data["dependencyPathNearSelected_" + str(i)] = self.doDependencyPathNearSelected(examples,i,featureNamesOnly)
		if "dependencyPathElements" in self.chosenFeatures:
		  	data["dependencyPathElements"] = self.doDependencyPathElements(examples,featureNamesOnly)
		if "bigrams" in self.chosenFeatures:
			data["bigrams"] = self.doBiGrams(examples,featureNamesOnly)

		if "selectedTokenTypes" in self.chosenFeatures:
			for i in range(self.argCount):
				data["selectedTokenTypes_" + str(i)] = self.doSelectedTokenTypes(examples,i,featureNamesOnly)		

		if featureNamesOnly:
			for id,strlist in data.items():
				assert isinstance(strlist,list)
			combined = sum(data.values(),[])
		else:
			# And combine the rest
			combined = hstack( [ d for d in data.values() if not d is None ] )

		return combined
	
	def corpusToVectors(self,corpus,featureNamesOnly,name,doTFIDF):
		vectorizerName = "%s_vectorizer" %  name
		tfidfName = "%s_tfidf" % name
		if featureNamesOnly:
			assert vectorizerName in self.tools
			featureNames = []
			for fn in self.tools[vectorizerName].get_feature_names():
				if fn is None:
					fn = u'None'
				elif isinstance(fn,tuple):
					fn = u"_".join(list(fn))
				featureNames.append(fn)
			return [ u"%s_%s" % (name,fname) for fname in featureNames ]
		else:
			if not vectorizerName in self.tools:
				self.tools[vectorizerName] = DictVectorizer()
				vecs = self.tools[vectorizerName].fit_transform(corpus)
				if doTFIDF:
					self.tools[tfidfName] = TfidfTransformer()
					vecs = self.tools[tfidfName].fit_transform(vecs)
				return vecs
			else:
				vecs = self.tools[vectorizerName].transform(corpus)
				if doTFIDF:
					vecs = self.tools[tfidfName].transform(vecs)
				return vecs
				
	#
	
	
	def doNgramsBetweenEntities(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			if len(example.arguments) != 2:
				return None

			sentenceid1,locs1 = example.arguments[0]
			sentenceid2,locs2 = example.arguments[1]
			if sentenceid1!=sentenceid2:
				return None
			
			sentence = example.sentences[sentenceid1]
			
			if min(locs2) > max(locs1):
				window = list(range(max(locs1)+1,min(locs2)))
			else:
				window = list(range(max(locs2)+1,min(locs1)))
				
			window = [ t for t in window if t >= 0 and t < len(sentence.tokens) ]
			tokens = [ sentence.tokens[t].word.lower() for t in window ]
			
			corpus.append(Counter(tokens))
		return self.corpusToVectors(corpus,featureNamesOnly,"ngrams_betweenentities",self.tfidf)
		
	def doSelectedTokenTypes(self,examples,argID,featureNamesOnly):
		corpus = []

		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence =  example.sentences[sentenceid]
			sentence.invertTriggers()

			type = 'None'
			key = tuple(locs)
			if key in sentence.locsToTriggerTypes:
				type = sentence.locsToTriggerTypes[key]
			corpus.append(Counter([type]))
		return self.corpusToVectors(corpus,featureNamesOnly,'selectedtokentypes_'+str(argID),False)

		
	def doBiGrams(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			allBigrams = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[i+1].word.lower()) for i in range(len(sentence.tokens)-1) ]
				allBigrams = allBigrams + bigrams
			
			corpus.append(Counter(allBigrams))
		return self.corpusToVectors(corpus,featureNamesOnly, 'bigrams', self.tfidf)
		
	def doDependencyPathNearSelected(self,examples,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,_ = example.arguments[argID]
			
			sameSentence = True
			for thisSID,_ in example.arguments:
				if sentenceid != thisSID:
					sameSentence = False
			#	assert sentenceid==thisSID, "Cannot deal with across sentence boundaries arguments"
			
			_,argLocs = example.arguments[argID]

			# Force single argument examples to use a path from enttity to root
			if len(example.arguments) == 1:
				sameSentence = False
				
			if sameSentence:
				sentence = example.sentences[sentenceid]
				locs = [ l for _,l in example.arguments ]
				locs = sum(locs, [])

				_,edges = sentence.extractMinSubgraphContainingNodes(locs)
			else:
				sentence = example.sentences[sentenceid]
				_,locs = example.arguments[argID]
				_,edges = sentence.extractSubgraphToRoot(locs)
			
			edges = [ (a,b) for a,b in edges if a in argLocs ]
			edgeTypes = sentence.getEdgeTypes(edges)
				
		
			corpus.append(Counter(edgeTypes))
			
			#sys.exit(0)
	
		return self.corpusToVectors(corpus,featureNamesOnly, 'dependencypathnearselectedtoken_' + str(argID), False)

	
	def doDependencyPathElements(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid0,_ = example.arguments[0]
			sameSentence = True
			for thisSID,_ in example.arguments:
				if sentenceid0 != thisSID:
					sameSentence = False
				#assert sentenceid==thisSID, "Cannot deal with across sentence boundaries arguments"

			# Force single argument examples to use a path from enttity to root
			if len(example.arguments) == 1:
				sameSentence = False
				
			if sameSentence:
				sentence = example.sentences[sentenceid0]
				locs = [ l for _,l in example.arguments ]
				locs = sum(locs, [])
				
				_,edges = sentence.extractMinSubgraphContainingNodes(locs)
				edgeTypes = sentence.getEdgeTypes(edges)
			else:
				edgeTypes = []
				for sentenceid,locs in example.arguments:
					sentence = example.sentences[sentenceid]
					_,edges = sentence.extractSubgraphToRoot(locs)
					edgeTypes += sentence.getEdgeTypes(edges)
					

			corpus.append(Counter(edgeTypes))
	
		return self.corpusToVectors(corpus,featureNamesOnly, 'dependencypathelements', False)

	def getTrainingVectors(self):
		return self.trainingVectors
		
	def __init__(self, corpus, candidates, featureChoice=None, tfidf=False):
		options = ["selectedTokenTypes","ngrams_betweenEntities","bigrams","dependencyPathElements","dependencyPathNearSelected"]

		if featureChoice is None:
			#self.chosenFeatures = ["selectedTokenTypes","dependencyPathElements"]
			self.chosenFeatures = ["selectedTokenTypes"]
		else:
			#assert isinstance(featureChoice, str)
			#self.chosenFeatures = sorted(list(set(featureChoice.split(','))))
			self.chosenFeatures = featureChoice
			
		for feature in self.chosenFeatures:
			assert feature in options, "Feature (%s) is not a valid feature" % feature
			
		self.tfidf = tfidf
		#self.argCount = len(examples[0].arguments)
		self.argCount = len(candidates[0].entityIDs)
		self.tools = {}
		self.trainingVectors = self.vectorize(corpus,candidates)


