
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import hstack
import itertools

import kindred

def _doEntityTypes(candidates,entityCount):
	data = []
	for cr in candidates:
		assert isinstance(cr,kindred.CandidateRelation)
		
		tokenInfo = {}
		for argI,entity in enumerate(cr.entities):
			argName = "selectedtokentypes_%d_%s" % (argI,entity.entityType)
			tokenInfo[argName] = 1
		data.append(tokenInfo)
	return data

def _doUnigramsBetweenEntities(candidates,entityCount):
	data = []	
	for cr in candidates:
		assert isinstance(cr,kindred.CandidateRelation)
		
		sentence = cr.sentence
		dataForThisCR = Counter()
		entityCount = len(cr.entities)
		entityToTokenIndices = { e:tokenIndices for e,tokenIndices in cr.sentence.entityAnnotations }
		
		for e1,e2 in itertools.combinations(range(entityCount),2):
			pos1 = entityToTokenIndices[cr.entities[e1]]
			pos2 = entityToTokenIndices[cr.entities[e2]]
			
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

def _doDependencyPathEdges(candidates,entityCount):
	data = []	
	for cr in candidates:
		assert isinstance(cr,kindred.CandidateRelation)
		sentence = cr.sentence
		entityToTokenIndices = { e:tokenIndices for e,tokenIndices in cr.sentence.entityAnnotations }
		
		entityCount = len(cr.entities)
		dataForThisCR = Counter()
		for e1,e2 in itertools.combinations(range(entityCount),2):
			pos1 = entityToTokenIndices[cr.entities[e1]]
			pos2 = entityToTokenIndices[cr.entities[e2]]

			combinedPos = pos1 + pos2
			
			basename = u"dependencypathelements"
			if entityCount > 2:
				basename = u"dependencypathelements_%d_%d" % (e1,e2)

			nodes,edges = sentence.extractMinSubgraphContainingNodes(combinedPos)
			for a,b,dependencyType in edges:
				dataForThisCR[u"%s_%s" % (basename,dependencyType)] += 1
		data.append(dataForThisCR)

	return data

def _doDependencyPathEdgesNearEntities(candidates,entityCount):
	data = []	
	for cr in candidates:
		assert isinstance(cr,kindred.CandidateRelation)
		sentence = cr.sentence
		entityToTokenIndices = { e:tokenIndices for e,tokenIndices in cr.sentence.entityAnnotations }
		
		dataForThisCR = Counter()

		allEntityLocs = []
		for e in cr.entities:
			allEntityLocs += entityToTokenIndices[e]
		
		nodes,edges = sentence.extractMinSubgraphContainingNodes(allEntityLocs)
		for i,e in enumerate(cr.entities):
			pos = entityToTokenIndices[e]

			for a,b,dependencyType in edges:
				if a in pos:
					dataForThisCR[u"dependencypathnearselectedtoken_%d_%s" % (i,dependencyType)] += 1
		data.append(dataForThisCR)

	return data

def _doBigrams(candidates,entityCount):
	data = []
	for cr in candidates:
		assert isinstance(cr,kindred.CandidateRelation)
		
		sentence = cr.sentence
		dataForThisCR = Counter()

		for _ in cr.entities:
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
		
	def _vectorize(self,candidates,fit):
		assert isinstance(candidates,list)
		assert len(candidates) > 0
		for c in candidates:
			assert isinstance(c,kindred.CandidateRelation)
			
		matrices = []
		for feature in self.chosenFeatures:
			assert feature in self.featureInfo.keys()
			featureFunction = self.featureInfo[feature]['func']
			never_tfidf = self.featureInfo[feature]['never_tfidf']
			data = featureFunction(candidates,self.entityCount)
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
			
	def fit_transform(self,candidates):
		"""
		Fit the vectorizer to a list of candidate relations found in a corpus and vectorize them to generate the feature matrix.
		
		:param candidates: Relation candidates to vectorize
		:type candidates: list of kindred.CandidateRelation
		:return: Feature matrix (# rows = number of candidate relations, # cols = number of features)
		:rtype: scipy.sparse.csr.csr_matrix
		"""
		assert self.fitted == False
		assert isinstance(candidates,list)
		assert len(candidates) > 0
		for c in candidates:
			assert isinstance(c,kindred.CandidateRelation)
		self.fitted = True
		return self._vectorize(candidates,True)
	
	def transform(self,candidates):
		"""
		Vectorize the candidate relations to generate the feature matrix. Must already have been fit.
		
		:param candidates: Relation candidates to vectorize
		:type candidates: list of kindred.CandidateRelation
		:return: Feature matrix (# rows = number of candidate relations, # cols = number of features)
		:rtype: scipy.sparse.csr.csr_matrix
		"""
		assert self.fitted == True
		assert isinstance(candidates,list)
		assert len(candidates) > 0
		for c in candidates:
			assert isinstance(c,kindred.CandidateRelation)
		return self._vectorize(candidates,False)
		
		
	
