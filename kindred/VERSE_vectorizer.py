import sys
import random
from SentenceModel import *
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

class Vectorizer:
	# Feature list
	# - ngrams for selected tokens
	# - ngrams for all tokens
	# - bigrams for all tokens
	# - ngrams for all tokens with POS
	# - ngrams for selected tokens with POS (or just POS?)
	# - bigrams on path from tokens to root
	
	def getFeatureNames(self):
		return self.vectorize(examples=[],featureNamesOnly=True)
	
	def vectorize(self,examples,featureNamesOnly=False):
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
		
		if "cooccurrences" in self.chosenFeatures:
			data["cooccurrences"] = self.doCooccurrences(examples,featureNamesOnly)


		if "summedWordvecs" in self.chosenFeatures:
			data["summedWordVecs"] = self.doSummedWordVecs(examples,featureNamesOnly)
		if "sparseWordvecs" in self.chosenFeatures:
			data["sparseWordVecs"] = self.doSparseWordVecs(examples,featureNamesOnly)
		if "summedWordvecsOfDependencyPath" in self.chosenFeatures:
			data["summedWordvecsOfDependencyPath"] = self.doSummedWordVecsOfDependencyPath(examples,featureNamesOnly)
		if "sparseWordvecsOfDependencyPath" in self.chosenFeatures:
			data["sparseWordvecsOfDependencyPath"] = self.doSparseWordVecsOfDependencyPath(examples,featureNamesOnly)
			
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
				print t
				assert isinstance(t,str)
		else:
			for id,thing in data.iteritems():
				if thing is None:
					print id, thing
				else:
					print id, thing.shape
			
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
				print name, fn
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
		
	def __init__(self, classes, examples, featureChoice=None, tfidf=False):
		assert len(classes) == len(examples)
		
		options = ["ngrams","selectedngrams","bigrams","ngramsPOS","selectedngramsPOS","ngramsOfDependencyPath","bigramsOfDependencyPath","selectedTokenTypes","lemmas","selectedlemmas","dependencyPathElements","dependencyPathNearSelected","summedWordvecs","sparseWordvecs","summedWordvecsOfDependencyPath","sparseWordvecsOfDependencyPath","splitAcrossSentences","skipgrams_2","skipgrams_3","skipgrams_4","skipgrams_5","skipgrams_6","skipgrams_7","skipgrams_8","skipgrams_9","skipgrams_10","cooccurrences","ngrams_betweenEntities","bigrams_betweenEntities"]
		
		for i in range(1,10):
			options.append("ngrams_entityWindowLeft_%d" % i)
			options.append("ngrams_entityWindowRight_%d" % i)
			options.append("ngrams_entityWindowBoth_%d" % i)
			options.append("bigrams_entityWindowBoth_%d" % i)
			
		for i in range(2,10):
			options.append("bigrams_entityWindowLeft_%d" % i)
			options.append("bigrams_entityWindowRight_%d" % i)
		
		if featureChoice is None:
			self.chosenFeatures = ["ngrams","selectedngrams","bigrams","ngramsPOS","selectedngramsPOS","bigramsOfDependencyPath","selectedTokenTypes","lemmas","selectedlemmas","dependencyPathElements","dependencyPathNearSelected","splitAcrossSentences","skipgrams_2"]
			#self.chosenFeatures = options
			#self.chosenFeatures = ["selectedngrams"]
		else:
			assert isinstance(featureChoice, str)
			self.chosenFeatures = sorted(list(set(featureChoice.split(','))))
			
		for feature in self.chosenFeatures:
			assert feature in options, "Feature (%s) is not a valid feature" % feature
			
		self.tfidf = tfidf
		self.argCount = len(examples[0].arguments)
		self.tools = {}
		self.wordVecsLoaded = False
		self.trainingVectors = self.vectorize(examples)


def buildClassifierWithSplit(classes, examples, featureChoice=None):
	#triggerClassifier = buildTriggerClassifier(positiveTriggerExamples, negativeTriggerExamples)
	
	print "Generating training and test set"
	random.seed(10)
	exampleIDsGroupedByClass = defaultdict(list)
	for i,c in enumerate(classes):
		exampleIDsGroupedByClass[c].append(i)
	
	allClasses = sorted(list(set(classes)))
	trainingIndices = []
	for c in allClasses:
		trainingSetSize = int(0.7 * len(exampleIDsGroupedByClass[c]))
		tmpTrainingIndices = random.sample(exampleIDsGroupedByClass[c], trainingSetSize)
		trainingIndices = trainingIndices + tmpTrainingIndices
	
	testingIndices = [ i for i in range(len(classes)) if not i in trainingIndices ]
	
	trainingClasses = [ classes[i] for i in trainingIndices ]
	trainingExamples = [ examples[i] for i in trainingIndices ]
	testingClasses = [ classes[i] for i in testingIndices ]
	testingExamples = [ examples[i] for i in testingIndices ]
			
	assert len(trainingClasses) == len(trainingExamples)
	assert len(testingClasses) == len(testingExamples)
	
	print "-"*30
	print len(trainingClasses),len(testingClasses)
	for c in allClasses:
		trainingCount = sum ( [ i==c for i in trainingClasses ] )
		testingCount = sum ( [ i==c for i in testingClasses ] )
		print c, trainingCount,testingCount
	for c in allClasses:
		assert c in trainingClasses, 'Class %d should be represented in training set (but is not). Need more data!' % c
		assert c in testingClasses, 'Class %d should be represented in testing set (but is not). Need more data!' % c
			
	print "Training set: %d examples (%d positive and %d negative)" % (len(trainingClasses),sum(trainingClasses),len(trainingClasses)-sum(trainingClasses))
	print "Testing set: %d examples (%d positive and %d negative)" % (len(testingClasses),sum(testingClasses),len(testingClasses)-sum(testingClasses))
	
	print "Starting vectorizer..."
	vectorizer = Vectorizer(trainingClasses,trainingExamples, featureChoice)
	trainingVectors = vectorizer.getTrainingVectors()
	print "Training vectors of size:", trainingVectors.shape
	
	#print trainingClasses
	#print trainingVectors
	#for c,example in zip(trainingClasses,trainingExamples):
	#	s = [ example.sentences[sentenceid].tokens[loc] for sentenceid,locs in example.arguments for loc in locs ]
	#	print ",".join(s)

	perc = 10
	weight = 10
	doTrim = False

	if doTrim:
		print "Trimming training vectors..."
		from sklearn.feature_selection import SelectKBest,SelectPercentile,chi2
		#featureSelector = SelectKBest(chi2, k=100)
		featureSelector = SelectPercentile(chi2,perc)
		trainingVectorsTrimmed = featureSelector.fit_transform(trainingVectors, trainingClasses)
		print "Trimmed training vectors of size:", trainingVectorsTrimmed.shape
	else:
		trainingVectorsTrimmed = trainingVectors
		featureSelector = None

	print "Creating SVM..."
	clf = svm.SVC(kernel='linear', class_weight={1: weight})
	#clf = svm.SVC()

	#print "Creating MultinomialNB..."
	#from sklearn.naive_bayes import MultinomialNB
	#clf = MultinomialNB(fit_prior=True)
	
	print "Fitting classifier to training data..."
	clf.fit(trainingVectorsTrimmed, trainingClasses)
	
	print "Vectorizing test data..."
	testingVectors = vectorizer.vectorize(testingExamples)

	if doTrim:
		print "Trimming test data..."
		testingVectorsTrimmed = featureSelector.transform(testingVectors)
	else:
		testingVectorsTrimmed = testingVectors
	
	print "Making predictions on test data..."
	predictions = clf.predict(testingVectorsTrimmed)
	
	print "perc=%d, weight=%d, doTrim=%s" % (perc,weight,doTrim)

	from sklearn.metrics import confusion_matrix
	print confusion_matrix(testingClasses, predictions)
	
	from sklearn.metrics import f1_score,precision_score,recall_score,classification_report
	print "f1_score: ", f1_score(testingClasses, predictions)
	print "precision_score: ", precision_score(testingClasses, predictions)
	print "recall_score: ", recall_score(testingClasses, predictions)
	#print classification_report(testingClasses,predictions)
	
	print "Fitting to entire training dataset"
	clf = svm.SVC(kernel='linear', class_weight={1: weight})
	clf.fit(vstack([trainingVectorsTrimmed,testingVectorsTrimmed]), trainingClasses+testingClasses)
	
	return vectorizer,featureSelector,clf

def buildVectorizer(classes, examples, parameters):
	featureChoice = None
	doFeatureSelection = False
	tfidf = False
	featureSelectPerc = 10
		
	if "featureChoice" in parameters:
		featureChoice = parameters["featureChoice"]
	if "doFeatureSelection" in parameters and parameters["doFeatureSelection"] == "True":
		doFeatureSelection = True
	if "featureSelectPerc" in parameters:
		featureSelectPerc = int(parameters["featureSelectPerc"])
	if "tfidf" in parameters and parameters["tfidf"] == "True":
		tfidf = True
		
	print "Starting vectorizer..."
	vectorizer = Vectorizer(classes,examples,featureChoice,tfidf)
	vectors = vectorizer.getTrainingVectors()
	print "Vectors of size:", vectors.shape

	if doFeatureSelection:
		print "Trimming training vectors..."
		from sklearn.feature_selection import SelectKBest,SelectPercentile,chi2
		#featureSelector = SelectKBest(chi2, k=100)`:
		featureSelector = SelectPercentile(chi2,featureSelectPerc)
		vectorsTrimmed = featureSelector.fit_transform(vectors, classes)
		vectorsTrimmed = coo_matrix(vectorsTrimmed)
		print "Trimmed training vectors of size:", vectorsTrimmed.shape
	else:
		vectorsTrimmed = vectors
		featureSelector = None

	return vectorsTrimmed,vectorizer,featureSelector

class MyLogisticRegression:
	def __init__(self,class_weight='auto', C=1.0, threshold=0.5):
		self.clf = LogisticRegression(class_weight=class_weight,C=C)
		self.threshold = threshold

	def fit(self,X,Y):
		self.clf.fit(X,Y)
		self.classes_ = self.clf.classes_

	def predictSimple(self,X,Y):
		return self.clf.predict(X)
	def predict_proba(self,X):
		return self.clf.predict_proba(X)
		
	def predict(self,X):
		probs = self.clf.predict_proba(X)

		# Ignore probabilities that fall below our threshold
		probs[probs<self.threshold] = -1.0

		# But make sure that the negative class (class=0) always has a slightly higher value
		probs[:,0][probs[:,0]<self.threshold] = -0.5

		# And get the highest probability for each row
		predictions = np.argmax(probs,axis=1)

		return predictions

def buildClassifierFromVectors(classes, vectors, parameters):
		
	class_weight_arg = 'auto'
	if "svmAutoClassWeights" in parameters and parameters["svmAutoClassWeights"] == "True":
		class_weight_arg = 'auto'
	elif "svmClassWeight" in parameters:
		allClasses = sorted(list(set(classes)))
		class_weight = parameters['svmClassWeight']
		#class_weight_arg = {1: weight}
		class_weight_arg = { c:class_weight for c in allClasses if c != 0 }

	print "-"*30
	print "SVM Parameters"
	print "-"*30
	for (a,b) in parameters.iteritems():
		print "%s:%s" % (a,b)
	print "-"*30
	
	classifier = 'SVM'
	if "classifier" in parameters:
		classifier = parameters["classifier"]

	print "Fitting to entire training dataset"

	if classifier == "SVM":
		clfParameterTypes = [('kernel',str),('C',float),('degree',int),('gamma',float),('coef0',float),('shrinking',bool)]
		clfParameters = { arg:type(parameters[arg]) for (arg,type) in clfParameterTypes if arg in parameters }

		clf = svm.SVC(class_weight=class_weight_arg, probability=True, **clfParameters)
	elif classifier == "LogisticRegression":
		clfParameterTypes = [('C',float),('threshold',float)]
		clfParameters = { arg:type(parameters[arg]) for (arg,type) in clfParameterTypes if arg in parameters }

		clf = MyLogisticRegression(class_weight=class_weight_arg, **clfParameters)
	elif classifier == "KNeighbors":
		clf = neighbors.KNeighborsClassifier(5, weights='uniform')
	else:
		raise RuntimeError("Unknown classifier type: %s" % classifier)

	clf.fit(vectors, classes)
	
	return clf

#def vectorizeSelectAndPredict(examples,vectorizer,featureSelector):
#	if featureSelector is None:
