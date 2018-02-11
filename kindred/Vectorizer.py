
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import hstack
import itertools

import kindred

def _doEntityTypes(corpus,entityCount):
	entityMapping = corpus.getEntityMapping()
	data = []
	for cr in corpus.getCandidateRelations(entityCount):
		tokenInfo = {}
		for argI,eID in enumerate(cr.entityIDs):
			eType = entityMapping[eID].entityType
			argName = "selectedtokentypes_%d_%s" % (argI,eType)
			tokenInfo[argName] = 1
		data.append(tokenInfo)
	return data

def _doUnigramsBetweenEntities(corpus,entityCount):
	data = []	
	for doc in corpus.documents:
		for sentence in doc.sentences:
			for cr,_ in sentence.candidateRelationsWithClasses[entityCount]:
				dataForThisCR = Counter()
				entityCount = len(cr.entityIDs)
				for e1,e2 in itertools.combinations(range(entityCount),2):
					#assert len(cr.entityIDs) == 2
					pos1 = sentence.entityIDToLoc[cr.entityIDs[e1]]
					pos2 = sentence.entityIDToLoc[cr.entityIDs[e2]]
					
					if max(pos1) < min(pos2):
						startPos,endPos = max(pos1)+1,min(pos2)
					else:
						startPos,endPos = max(pos2)+1,min(pos1)

					tokenData = [ sentence.tokens[i].word.lower() for i in range(startPos,endPos) ]

					basename = u"ngrams_betweenentities"
					if entityCount > 2:
						basename = u"ngrams_betweenentities_%d_%d" % (e1,e2)

					for t in tokenData:
						dataForThisCR[u"%s_%s" % (basename,t)] += 1
				data.append(dataForThisCR)

	return data

def _doDependencyPathEdges(corpus,entityCount):
	data = []	
	for doc in corpus.documents:
		for sentence in doc.sentences:
			for cr,_ in sentence.candidateRelationsWithClasses[entityCount]:
				
				entityCount = len(cr.entityIDs)
				dataForThisCR = Counter()
				for e1,e2 in itertools.combinations(range(entityCount),2):

				
					pos1 = sentence.entityIDToLoc[cr.entityIDs[e1]]
					pos2 = sentence.entityIDToLoc[cr.entityIDs[e2]]

					combinedPos = pos1 + pos2
					
					basename = u"dependencypathelements"
					if entityCount > 2:
						basename = u"dependencypathelements_%d_%d" % (e1,e2)

					nodes,edges = sentence.extractMinSubgraphContainingNodes(combinedPos)
					for a,b,dependencyType in edges:
						dataForThisCR[u"%s_%s" % (basename,dependencyType)] += 1
				data.append(dataForThisCR)

	return data

def _doDependencyPathEdgesNearEntities(corpus,entityCount):
	data = []	
	for doc in corpus.documents:
		for sentence in doc.sentences:
			for cr,_ in sentence.candidateRelationsWithClasses[entityCount]:
				dataForThisCR = Counter()

				allEntityLocs = []
				for eID in cr.entityIDs:
					allEntityLocs += sentence.entityIDToLoc[eID]
				
				nodes,edges = sentence.extractMinSubgraphContainingNodes(allEntityLocs)
				for i,eID in enumerate(cr.entityIDs):

					pos = sentence.entityIDToLoc[eID]

					for a,b,dependencyType in edges:
						if a in pos:
							dataForThisCR[u"dependencypathnearselectedtoken_%d_%s" % (i,dependencyType)] += 1
				data.append(dataForThisCR)

	return data

def _doBigrams(corpus,entityCount):
	data = []	
	for doc in corpus.documents:
		for sentence in doc.sentences:
			for cr,_ in sentence.candidateRelationsWithClasses[entityCount]:
				dataForThisCR = Counter()

				for _ in cr.entityIDs:

					startPos = 0
					endPos = len(sentence.tokens)

					tokenData = [ (sentence.tokens[i].word.lower(),sentence.tokens[i+1].word.lower()) for i in range(startPos,endPos-1) ]
					for t in tokenData:
						dataForThisCR[u"bigrams_%s_%s" % t] += 1
				data.append(dataForThisCR)

	return data

class Vectorizer:
	"""
	Vectorizes set of candidate relations into scipy sparse matrix.
	"""
	
	def __init__(self,entityCount=2,featureChoice=None,tfidf=True):
		"""
		Constructor for vectorizer class with options for what features to use and whether to normalize using TFIDF
		
		:param entityCount: Number of entities in candidate relations to vectorize
		:param featureChoice: List of features (can be one or a set of the following: 'entityTypes', 'unigramsBetweenEntities', 'bigrams', 'dependencyPathEdges', 'dependencyPathEdgesNearEntities'). Set as None to use all of them. 
		:param tfidf: Whether to normalize n-gram based features using term frequency-inverse document frequency
		:type entityCount: int
		:type featureChoice: list of str
		:type tfidf: bool
		"""
		
		self.fitted = False

		assert isinstance(entityCount, int)
		self.entityCount = entityCount
		
		self._registerFunctions()
		validFeatures = self.featureInfo.keys()

		if featureChoice is None:
			self.chosenFeatures = ['entityTypes','unigramsBetweenEntities','bigrams','dependencyPathEdges','dependencyPathEdgesNearEntities']
		else:
			assert isinstance(featureChoice,list)
			for f in featureChoice:
				assert f in validFeatures, "Feature (%s) is not a valid feature" % f
			self.chosenFeatures = featureChoice
		
		self.tfidf = tfidf


		self.dictVectorizers = {}
		self.tfidfTransformers = {}

	def _registerFunctions(self):
		self.featureInfo = {}
		self.featureInfo['entityTypes'] = {'func':_doEntityTypes,'never_tfidf':True}
		self.featureInfo['unigramsBetweenEntities'] = {'func':_doUnigramsBetweenEntities,'never_tfidf':False}
		self.featureInfo['bigrams'] = {'func':_doBigrams,'never_tfidf':False}
		self.featureInfo['dependencyPathEdges'] = {'func':_doDependencyPathEdges,'never_tfidf':True}
		self.featureInfo['dependencyPathEdgesNearEntities'] = {'func':_doDependencyPathEdgesNearEntities,'never_tfidf':True}
				
	def getFeatureNames(self):
		"""
		Get the names for each feature (i.e. each column in matrix generated by the fit_transform() and transform() functions. Fit_transform() must have already been used, i.e. the vectorizer needs to have been fit to training data.
		
		:return: List of names for each feature (column of the vectorized data)
		:rtype: List of str
		"""
		
		assert self.fitted == True, "Must have fit data first"
		featureNames = []
		for feature in self.chosenFeatures:
			if feature in self.dictVectorizers:
				featureNames += self.dictVectorizers[feature].get_feature_names()
		return featureNames
		



	def _vectorize(self,corpus,fit):
		assert isinstance(corpus,kindred.Corpus)
			
		matrices = []
		for feature in self.chosenFeatures:
			assert feature in self.featureInfo.keys()
			featureFunction = self.featureInfo[feature]['func']
			never_tfidf = self.featureInfo[feature]['never_tfidf']
			data = featureFunction(corpus,self.entityCount)
			notEmpty = any( len(d)>0 for d in data )
			if fit:
				if notEmpty:
					self.dictVectorizers[feature] = DictVectorizer()
					if self.tfidf and not never_tfidf:
						self.tfidfTransformers[feature] = TfidfTransformer()
						intermediate = self.dictVectorizers[feature].fit_transform(data)
						matrices.append(self.tfidfTransformers[feature].fit_transform(intermediate))
					else:
						matrices.append(self.dictVectorizers[feature].fit_transform(data))
			else:
				if feature in self.dictVectorizers:
					if self.tfidf and not never_tfidf:
						intermediate = self.dictVectorizers[feature].transform(data)
						matrices.append(self.tfidfTransformers[feature].transform(intermediate))
					else:
						matrices.append(self.dictVectorizers[feature].transform(data))

		mergedMatrix = hstack(matrices)
		return mergedMatrix
			
	def fit_transform(self,corpus):
		"""
		Fit the vectorizer to a training corpus (using the candidate relations found in the corpus) and vectorize the candidate relations to generate the feature matrix.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		:return: Feature matrix (# rows = number of candidate relations, # cols = number of features)
		:rtype: scipy.sparse.csr.csr_matrix
		"""
		assert self.fitted == False
		assert len(corpus.getCandidateRelations(self.entityCount)) > 0, "No candidate (%d-ary) relations found in corpus" % self.entityCount
		self.fitted = True
		return self._vectorize(corpus,True)
	
	def transform(self,corpus):
		"""
		Vectorize the candidate relations to generate the feature matrix. Must already have been fit.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		:return: Feature matrix (# rows = number of candidate relations, # cols = number of features)
		:rtype: scipy.sparse.csr.csr_matrix
		"""
		assert self.fitted == True
		assert len(corpus.getCandidateRelations(self.entityCount)) > 0, "No candidate (%d-ary) relations found in corpus" % self.entityCount
		return self._vectorize(corpus,False)
		
		
	
