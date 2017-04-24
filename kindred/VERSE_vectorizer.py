import sys
import random
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

		#print "-"*30
		#print [ (i,t) for i,t in enumerate(self.tokens) ]
		#print
		#print self.dependencies
		#print
		#print self.predictedEntityLocs
		#print self.knownEntityLocs
		#print
		#print minSet
		#self.printDependencyGraph()
		#print "-"*30

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
		#print "MOO"
	
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

def ProcessedSentenceToVerseSentence(s):
	assert isinstance(s,kindred.ProcessedSentence)
	argTypes = { e.entityID:e.entityType for e in s.processedEntities }
	argLocs = { e.entityID:e.entityLocs for e in s.processedEntities }
	#def __init__(self, tokens, dependencies, eventTriggerLocs, eventTriggerTypes, argumentTriggerLocs, argumentTriggerTypes):

	verseS = SentenceModel(s.tokens,s.dependencies,{},{},argLocs,argTypes)

	return verseS

def CandidateRelationToExample(r):
	assert isinstance(r,kindred.CandidateRelation)

	eID_to_locs = { e.entityID:e.entityLocs for e in r.processedSentence.processedEntities }
	s = ProcessedSentenceToVerseSentence(r.processedSentence)
	locs = [ eID_to_locs[eID] for eID in r.entitiesInRelation ]
	example = Example("None",[s],locs)

	return example
			
class VERSEVectorizer:
	# Feature list
	# - ngrams for selected tokens
	# - ngrams for all tokens
	# - bigrams for all tokens
	# - ngrams for all tokens with POS
	# - ngrams for selected tokens with POS (or just POS?)
	# - bigrams on path from tokens to root
	
	def getFeatureNames(self):
		return self.vectorize(examples=[],featureNamesOnly=True)
	
	def vectorize(self,candidates,featureNamesOnly=False):
		examples = [ CandidateRelationToExample(c) for c in candidates ]

		assert len(examples) > 0, "Expected more than zero examples to vectorize"
		for e in examples:
			assert self.argCount == len(e.arguments), 'All examples must have the same number of arguments (%d)' % self.argCount
			
		data = OrderedDict()
		if "splitAcrossSentences" in self.chosenFeatures:
			data["splitAcrossSentences"] = self.doSplitAcrossSentences(examples,featureNamesOnly)
		if "ngrams" in self.chosenFeatures:
			#print "    doing ngrams..."
			data["ngrams"] = self.doNGrams(examples,featureNamesOnly)
			
		if "skipgrams_2" in self.chosenFeatures:
			data["skipgrams_2"] = self.doSkipGrams(examples,2,featureNamesOnly)
		if "skipgrams_3" in self.chosenFeatures:
			data["skipgrams_3"] = self.doSkipGrams(examples,3,featureNamesOnly)
		if "skipgrams_4" in self.chosenFeatures:
			data["skipgrams_4"] = self.doSkipGrams(examples,4,featureNamesOnly)
		if "skipgrams_5" in self.chosenFeatures:
			data["skipgrams_5"] = self.doSkipGrams(examples,5,featureNamesOnly)
		if "skipgrams_6" in self.chosenFeatures:
			data["skipgrams_6"] = self.doSkipGrams(examples,6,featureNamesOnly)
		if "skipgrams_7" in self.chosenFeatures:
			data["skipgrams_7"] = self.doSkipGrams(examples,7,featureNamesOnly)
		if "skipgrams_8" in self.chosenFeatures:
			data["skipgrams_8"] = self.doSkipGrams(examples,8,featureNamesOnly)
		if "skipgrams_9" in self.chosenFeatures:
			data["skipgrams_9"] = self.doSkipGrams(examples,9,featureNamesOnly)
		if "skipgrams_10" in self.chosenFeatures:
			data["skipgrams_10"] = self.doSkipGrams(examples,10,featureNamesOnly)
			
		for j in range(1,10):
			if ("ngrams_entityWindowLeft_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("ngrams_entityWindowLeft_%d_%d" % (j,i))] = self.doNGramsEntityWindowLeft(examples,j,i,featureNamesOnly)
		for j in range(1,10):
			if ("ngrams_entityWindowRight_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("ngrams_entityWindowRight_%d_%d" % (j,i))] = self.doNGramsEntityWindowRight(examples,j,i,featureNamesOnly)
		for j in range(1,10):
			if ("ngrams_entityWindowBoth_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("ngrams_entityWindowBoth_%d_%d" % (j,i))] = self.doNGramsEntityWindowBoth(examples,j,i,featureNamesOnly)
					
		for j in range(1,10):
			if ("bigrams_entityWindowLeft_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("bigrams_entityWindowLeft_%d_%d" % (j,i))] = self.doBigramsEntityWindowLeft(examples,j,i,featureNamesOnly)
		for j in range(1,10):
			if ("bigrams_entityWindowRight_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("bigrams_entityWindowRight_%d_%d" % (j,i))] = self.doBigramsEntityWindowRight(examples,j,i,featureNamesOnly)
		for j in range(1,10):
			if ("bigrams_entityWindowBoth_%d" % j) in self.chosenFeatures:
				for i in range(self.argCount):
					data[("bigrams_entityWindowBoth_%d_%d" % (j,i))] = self.doBigramsEntityWindowBoth(examples,j,i,featureNamesOnly)
					
		if "ngrams_betweenEntities" in self.chosenFeatures:
			data["ngrams_betweenEntities"] = self.doNgramsBetweenEntities(examples,featureNamesOnly)
		if "bigrams_betweenEntities" in self.chosenFeatures:
			data["bigrams_betweenEntities"] = self.doBigramsBetweenEntities(examples,featureNamesOnly)
		
		if "selectedngrams" in self.chosenFeatures:
			#print "    doing selected ngrams..."
			for i in range(self.argCount):
				data["selectedngrams_" + str(i)] = self.doNGramsOfArguments(examples,i,featureNamesOnly)
		#"dependencyPathNearSelected"
		if "dependencyPathNearSelected" in self.chosenFeatures:
			for i in range(self.argCount):
				data["dependencyPathNearSelected_" + str(i)] = self.doDependencyPathNearSelected(examples,i,featureNamesOnly)
		if "dependencyPathElements" in self.chosenFeatures:
		  	data["dependencyPathElements"] = self.doDependencyPathElements(examples,featureNamesOnly)
		if "lemmas" in self.chosenFeatures:
			#print "    doing ngrams..."
			data["lemmas"] = self.doLemmas(examples,featureNamesOnly)
		if "selectedlemmas" in self.chosenFeatures:
			#print "    doing selected ngrams..."
			for i in range(self.argCount):
				data["selectedlemmas_" + str(i)] = self.doLemmasOfArguments(examples,i,featureNamesOnly)
		if "bigrams" in self.chosenFeatures:
			#print "    doing bigrams..."
			data["bigrams"] = self.doBiGrams(examples,featureNamesOnly)
		if "ngramsPOS" in self.chosenFeatures:
			#print "    doing ngrams with POS..."
			data["ngramsPOS"] = self.doNGramsWithPOS(examples,featureNamesOnly)
		if "selectedngramsPOS" in self.chosenFeatures:
			#print "    doing selected ngrams with POS..."
			for i in range(self.argCount):
				data["selectedngramsPOS_" + str(i)] = self.doNGramsOfArgumentsWithPOS(examples,i,featureNamesOnly)

		if "selectedTokenTypes" in self.chosenFeatures:
			for i in range(self.argCount):
				data["selectedTokenTypes_" + str(i)] = self.doSelectedTokenTypes(examples,i,featureNamesOnly)		

		if "ngramsOfDependencyPath" in self.chosenFeatures:
			data["ngramsOfDependencyPath"] = self.doNGramsOfDependencyPath(examples,featureNamesOnly)
		if "bigramsOfDependencyPath" in self.chosenFeatures:
			data["bigramsOfDependencyPath"] = self.doBiGramsOfDependencyPath(examples,featureNamesOnly)

		# Let's randomly through out some feature sets
		#if not hasattr(self, 'randomDeletions'):
		#	self.randomDeletions = random.sample(data.keys(), random.randint(0,len(data)-1))
		#for rd in self.randomDeletions:
		#	del data[rd]
		#print data.keys()
		if featureNamesOnly:
			for id,strlist in data.iteritems():
				assert isinstance(strlist,list)
			combined = sum(data.values(),[])
			for t in combined:
				print(t)
				assert isinstance(t,str)
		else:
			#for id,thing in data.iteritems():
			#	if thing is None:
			#		print id, thing
			#	else:
			#		print id, thing.shape
			
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
				print(name, fn)
				if fn is None:
					fn = u'None'
				elif isinstance(fn,tuple):
					fn = u"_".join(list(fn))
				featureNames.append(fn)
			#featureNames = [ fn if not fn is None else u"NONE" for fn in featureNames ]
			#for fn in featureNames:
			#	print name, fn
			return [ "%s_%s" % (name,fname.encode('utf8')) for fname in featureNames ]
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
		return self.corpusToVectors(corpus,featureNamesOnly,"ngrams_betweenEntites",self.tfidf)
		
		
	def doBigramsBetweenEntities(self,examples,featureNamesOnly):
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
			bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[j].word.lower()) for i,j in zip(window,window[1:]) ]
			corpus.append(Counter(bigrams))
			
		return self.corpusToVectors(corpus,featureNamesOnly,"ngrams_betweenEntites",self.tfidf)
	
	
	def doBigramsEntityWindowLeft(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			minL = min(locs)
			leftWindow = list(range(minL-windowSize,minL))
			leftWindow = [ t for t in leftWindow if t >= 0 and t < len(sentence.tokens) ]
			bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[j].word.lower()) for i,j in zip(leftWindow,leftWindow[1:]) ]
			corpus.append(Counter(bigrams))
		name = "Bigrams_EntityWindowLeft_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)
		
	def doBigramsEntityWindowRight(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			maxL = max(locs)
			rightWindow = list(range(maxL+1,maxL+windowSize+1))
			rightWindow = [ t for t in rightWindow if t >= 0 and t < len(sentence.tokens) ]
			bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[j].word.lower()) for i,j in zip(rightWindow,rightWindow[1:]) ]
			corpus.append(Counter(bigrams))
			
		name = "Bigrams_EntityWindowRight_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)
		
	def doBigramsEntityWindowBoth(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			minL,maxL = min(locs),max(locs)
			leftWindow = list(range(minL-windowSize,minL))
			rightWindow = list(range(maxL+1,maxL+windowSize+1))
			bothWindows = leftWindow + rightWindow
			bothWindows = [ t for t in bothWindows if t >= 0 and t < len(sentence.tokens) ]
			bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[j].word.lower()) for i,j in zip(bothWindows,bothWindows[1:]) ]
			corpus.append(Counter(bigrams))
			
		name = "Bigrams_EntityWindowBoth_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)
	
	def doNGramsEntityWindowLeft(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			minL = min(locs)
			leftWindow = list(range(minL-windowSize,minL))
			leftWindow = [ t for t in leftWindow if t >= 0 and t < len(sentence.tokens) ]
			tokens = [ sentence.tokens[t].word.lower() for t in leftWindow ]
			
			corpus.append(Counter(tokens))
		name = "Ngrams_EntityWindowLeft_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)
		
	def doNGramsEntityWindowRight(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			maxL = max(locs)
			rightWindow = list(range(maxL+1,maxL+windowSize+1))
			rightWindow = [ t for t in rightWindow if t >= 0 and t < len(sentence.tokens) ]
			tokens = [ sentence.tokens[t].word.lower() for t in rightWindow ]
			
			corpus.append(Counter(tokens))
		name = "Ngrams_EntityWindowRight_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)
		
	def doNGramsEntityWindowBoth(self,examples,windowSize,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			
			minL,maxL = min(locs),max(locs)
			leftWindow = list(range(minL-windowSize,minL))
			rightWindow = list(range(maxL+1,maxL+windowSize+1))
			bothWindows = leftWindow + rightWindow
			bothWindows = [ t for t in bothWindows if t >= 0 and t < len(sentence.tokens) ]
			tokens = [ sentence.tokens[t].word.lower() for t in bothWindows ]
			
			corpus.append(Counter(tokens))
		name = "Ngrams_EntityWindowBoth_%d_%d" % (windowSize,argID)
		return self.corpusToVectors(corpus,featureNamesOnly,name,self.tfidf)

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
		return self.corpusToVectors(corpus,featureNamesOnly,'SelectedTokenTypes_'+str(argID),False)

	def doTypesNearSelectedTokens(self,examples,distance):
		corpus = []

		for example in examples:
			# Get all the neighbours of all the selected tokens
			selectedTokens = sum(example.argTokenGroups,[])
			neighbours = sum ([[ t-distance,t+distance ] for t in selectedTokens ], [])
			# Get all the types of these tokens
			types = [ example.knownTriggerTypesByLoc[n] for n in neighbours if n in example.knownTriggerTypesByLoc ]

			# Convert the list of types to a dictionary of counts for use by the vectorizer
			corpus.append(Counter(types))
		return self.corpusToVectors(corpus,featureNamesOnly,'TypesNearSelectedTokens',False)
		
	def doTypesNearSelectedTokensWithDependencies(self,examples,distance):
		corpus = []

		for example in examples:
			if distance == 1:
				neighbourList = example.dep_neighbours
			elif distance == 2:
				neighbourList = example.dep_neighbours2
			else:
				raise RuntimeError("Expecting distance to be 1 or 2")

			# Get all the neighbours of all the selected tokens
			selectedTokens = sum(example.argTokenGroups,[])
			neighbours = sum ([ list(neighbourList[t]) for t in selectedTokens ], [])
			# Get all the types of these tokens
			types = [ example.knownTriggerTypesByLoc[n] for n in neighbours if n in example.knownTriggerTypesByLoc ]

			# Convert the list of types to a dictionary of counts for use by the vectorizer
			corpus.append(Counter(types))
		return self.corpusToVectors(corpus,featureNamesOnly,'TypesNearSelectedTokensWithDependencies',False)

	def doLemmasOfArguments(self,examples,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			tokens = [ sentence.tokens[t].lemma.lower() for t in locs ]
			corpus.append(Counter(tokens))
		return self.corpusToVectors(corpus,featureNamesOnly,'LemmasOfArguments_'+str(argID),self.tfidf)
		
	def doNGramsOfArguments(self,examples,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			tokens = [ sentence.tokens[t].word.lower() for t in locs ]
			corpus.append(Counter(tokens))
		return self.corpusToVectors(corpus,featureNamesOnly,'NGramsOfArguments_'+str(argID),self.tfidf)
	
	def doNGramsOfArgumentsWithPOS(self,examples,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,locs = example.arguments[argID]
			sentence = example.sentences[sentenceid]
			tokensWithPOS = [ (sentence.tokens[t].word.lower(),sentence.tokens[t].partofspeech) for t in locs ]
			corpus.append(Counter(tokensWithPOS))
		return self.corpusToVectors(corpus,featureNamesOnly,'NGramsOfArgumentsWithPOS_'+str(argID),self.tfidf)	

	def doNGrams(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			allTokens = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				tokens = [ t.word.lower() for t in sentence.tokens ]
				allTokens = allTokens + tokens
			corpus.append(Counter(allTokens))
		return self.corpusToVectors(corpus,featureNamesOnly, 'NGrams', self.tfidf)

	def doLemmas(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			allTokens = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				tokens = [ t.lemma.lower() for t in sentence.tokens ]
				allTokens = allTokens + tokens
			corpus.append(Counter(allTokens))
		return self.corpusToVectors(corpus,featureNamesOnly, 'Lemmas', self.tfidf)


	def doNGramsWithPOS(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			allTokensWithPOS = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				tokensWithPOS = [ (t.word.lower(),t.partofspeech) for t in sentence.tokens ]
				allTokensWithPOS = allTokensWithPOS + tokensWithPOS
			corpus.append(Counter(allTokensWithPOS))
		return self.corpusToVectors(corpus,featureNamesOnly, 'NGramsWithPOS', self.tfidf)

		
	def doBiGrams(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			allBigrams = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				bigrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[i+1].word.lower()) for i in xrange(len(sentence.tokens)-1) ]
				allBigrams = allBigrams + bigrams
			
			corpus.append(Counter(allBigrams))
		return self.corpusToVectors(corpus,featureNamesOnly, 'BiGrams', self.tfidf)
		
	def doSkipGrams(self,examples,gap,featureNamesOnly):
		corpus = []
		for example in examples:
			allSkipgrams = []
			for sentenceid,_ in example.arguments:
				sentence = example.sentences[sentenceid]
				skipgrams = [ (sentence.tokens[i].word.lower(),sentence.tokens[i+gap].word.lower()) for i in xrange(len(sentence.tokens)-gap) ]
				allSkipgrams = allSkipgrams + skipgrams
			
			corpus.append(Counter(allSkipgrams))
		return self.corpusToVectors(corpus,featureNamesOnly, 'SkipGrams_%d' % gap, self.tfidf)
	
	def doSplitAcrossSentences(self,examples,featureNamesOnly):
		if featureNamesOnly:
			return ["splitAcrossSentences"]
	
		out = lil_matrix((len(examples),1))
		for i,example in enumerate(examples):
			sentenceid0,_ = example.arguments[0]
			sameSentence = True
			for thisSID,_ in example.arguments:
				if sentenceid0 != thisSID:
					sameSentence = False
					break
					
			if not sameSentence:
				out[i,0] = 1
					
		return coo_matrix(out)
	
	def doDependencyPathNearSelected(self,examples,argID,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid,_ = example.arguments[argID]
			#print example.sentences[sentenceid].dependencies
			#print "-"*30
			#print example.sentences[sentenceid]
			#print "-"*30
			#example.sentences[sentenceid].printDependencyGraph()
			#print "-"*30
			
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
	
		#print corpus
		return self.corpusToVectors(corpus,featureNamesOnly, 'DependencyPathNearSelectedToken_' + str(argID), False)

	
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
				#print "EX:", example, sorted(edgeTypes)
				#print "EX:", "-"*30
				#for edgeType in edgeTypes:
				#	print "EDGE", edgeType
			else:
				edgeTypes = []
				for sentenceid,locs in example.arguments:
					sentence = example.sentences[sentenceid]
					_,edges = sentence.extractSubgraphToRoot(locs)
					edgeTypes += sentence.getEdgeTypes(edges)
					
			#print [ t.word for t in sentence.tokens ]
			#print locs,edges,edgeTypes

			corpus.append(Counter(edgeTypes))
			
			#sys.exit(0)
	
		#print corpus
		#sys.exit(255)
		return self.corpusToVectors(corpus,featureNamesOnly, 'DependencyPathElements', False)

	def doNGramsOfDependencyPath(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid0,_ = example.arguments[0]
			sameSentence = True
			for thisSID,_ in example.arguments:
				if sentenceid0 != thisSID:
					sameSentence = False
		
			# Force single argument examples to use a path from enttity to root
			if len(example.arguments) == 1:
				sameSentence = False

			if sameSentence:
				sentence = example.sentences[sentenceid0]
				locs = [ l for _,l in example.arguments ]
				locs = sum(locs, [])
				
				nodes,_ = sentence.extractMinSubgraphContainingNodes(locs)

				ngrams = [ sentence.tokens[a].word.lower() for a in nodes ]
			else:
				ngrams = []
				for sentenceid,locs in example.arguments:
					sentence = example.sentences[sentenceid]
					nodes,_ = sentence.extractSubgraphToRoot(locs)
					tmpNgrams = [ sentence.tokens[a].word.lower() for a in nodes ]
					ngrams += tmpNgrams
			
			corpus.append(Counter(ngrams))
			
		return self.corpusToVectors(corpus,featureNamesOnly, 'NGramsOfDependencyPath', self.tfidf)
		
	def doBiGramsOfDependencyPath(self,examples,featureNamesOnly):
		corpus = []
		for example in examples:
			sentenceid0,_ = example.arguments[0]
			sameSentence = True
			for thisSID,_ in example.arguments:
				if sentenceid0 != thisSID:
					sameSentence = False
			
			# Force single argument examples to use a path from enttity to root
			if len(example.arguments) == 1:
				sameSentence = False

			if sameSentence:
				sentence = example.sentences[sentenceid0]
				#print '-'*30
				#print sentence
				#print '-'*30
				#sentence.printDependencyGraph()
				#print '-'*30
				#sys.exit(0)
				
				locs = [ l for _,l in example.arguments ]
				locs = sum(locs, [])
				
				_,edges = sentence.extractMinSubgraphContainingNodes(locs)

				bigrams = [ (sentence.tokens[a].word.lower(),sentence.tokens[b].word.lower()) for a,b in edges ]
			else:
				bigrams = []
				for sentenceid,locs in example.arguments:
					sentence = example.sentences[sentenceid]
					_,edges = sentence.extractSubgraphToRoot(locs)
					tmpBigrams = [ (sentence.tokens[a].word.lower(),sentence.tokens[b].word.lower()) for a,b in edges ]
					bigrams += tmpBigrams
			
			corpus.append(Counter(bigrams))
			
		return self.corpusToVectors(corpus,featureNamesOnly, 'BiGramsOfDependencyPath', self.tfidf)
		
	def getTrainingVectors(self):
		return self.trainingVectors
		
	def __init__(self, candidates, featureChoice=None, tfidf=False):
		#assert isinstance(candidates)
		#for c in candidates:
		#	assert isinstance(c,kindred.CandidateRelation)
		
		options = ["ngrams","selectedngrams","bigrams","ngramsPOS","selectedngramsPOS","ngramsOfDependencyPath","bigramsOfDependencyPath","selectedTokenTypes","lemmas","selectedlemmas","dependencyPathElements","dependencyPathNearSelected","splitAcrossSentences","skipgrams_2","skipgrams_3","skipgrams_4","skipgrams_5","skipgrams_6","skipgrams_7","skipgrams_8","skipgrams_9","skipgrams_10","ngrams_betweenEntities","bigrams_betweenEntities"]
		
		for i in range(1,10):
			options.append("ngrams_entityWindowLeft_%d" % i)
			options.append("ngrams_entityWindowRight_%d" % i)
			options.append("ngrams_entityWindowBoth_%d" % i)
			options.append("bigrams_entityWindowBoth_%d" % i)
			
		for i in range(2,10):
			options.append("bigrams_entityWindowLeft_%d" % i)
			options.append("bigrams_entityWindowRight_%d" % i)
		
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
		self.argCount = len(candidates[0].entitiesInRelation)
		self.tools = {}
		self.trainingVectors = self.vectorize(candidates)


