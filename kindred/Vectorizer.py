
from collections import Counter,OrderedDict
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import coo_matrix, csr_matrix, lil_matrix, hstack, vstack

import kindred

class Vectorizer:
	"""
	Vectorizes set of candidate relations into scipy sparse matrix.
	"""
	
	def __init__(self,featureChoice=None,tfidf=True):
		self.fitted = False
		
		self._registerFunctions()
		validFeatures = self.featureInfo.keys()

		if featureChoice is None:
			self.chosenFeatures = validFeatures
		else:
			for f in featureChoice:
				assert f in validFeatures, "Feature (%s) is not a valid feature" % f
			self.chosenFeatures = featureChoice
		
		self.tfidf = tfidf


		self.dictVectorizers = {}
		self.tfidfTransformers = {}

	def _registerFunctions(self):
		self.featureInfo = OrderedDict()
		self.featureInfo['entityTypes'] = {'func':Vectorizer.doEntityTypes,'never_tfidf':True}
		self.featureInfo['unigramsBetweenEntities'] = {'func':Vectorizer.doUnigramsBetweenEntities,'never_tfidf':False}
		self.featureInfo['bigrams'] = {'func':Vectorizer.doBigrams,'never_tfidf':False}
		self.featureInfo['dependencyPathEdges'] = {'func':Vectorizer.doDependencyPathEdges,'never_tfidf':True}
		self.featureInfo['dependencyPathEdgesNearEntities'] = {'func':Vectorizer.doDependencyPathEdgesNearEntities,'never_tfidf':True}
		
	def getFeatureNames(self):
		assert self.fitted == True, "Must have fit data first"
		featureNames = []
		for feature in self.chosenFeatures:
			featureNames += self.dictVectorizers[feature].get_feature_names()
		return featureNames
		

	def doEntityTypes(self,corpus):
		entityMapping = corpus.getEntityMapping()
		data = []
		for cr in corpus.getCandidateRelations():
			tokenInfo = {}
			for argI,eID in enumerate(cr.entityIDs):
				eType = entityMapping[eID].entityType
				argName = "selectedtokentypes_%d_%s" % (argI,eType)
				tokenInfo[argName] = 1
			data.append(tokenInfo)
		return data
	
	def doUnigramsBetweenEntities(self,corpus):
		entityMapping = corpus.getEntityMapping()
		data = []	
		for doc in corpus.documents:
			for sentence in doc.sentences:
				for cr,_ in sentence.candidateRelationsWithClasses:
					dataForThisCR = Counter()

					assert len(cr.entityIDs) == 2
					pos1 = sentence.entityIDToLoc[cr.entityIDs[0]]
					pos2 = sentence.entityIDToLoc[cr.entityIDs[1]]
					
					if max(pos1) < min(pos2):
						startPos,endPos = max(pos1)+1,min(pos2)
					else:
						startPos,endPos = max(pos2)+1,min(pos1)

					tokenData = [ sentence.tokens[i].word.lower() for i in range(startPos,endPos) ]
					for t in tokenData:
						dataForThisCR[u"ngrams_betweenentities_%s" % t] += 1
					data.append(dataForThisCR)

		return data
	
	def doDependencyPathEdges(self,corpus):
		entityMapping = corpus.getEntityMapping()
		data = []	
		for doc in corpus.documents:
			for sentence in doc.sentences:
				for cr,_ in sentence.candidateRelationsWithClasses:
					dataForThisCR = Counter()

					assert len(cr.entityIDs) == 2
					pos1 = sentence.entityIDToLoc[cr.entityIDs[0]]
					pos2 = sentence.entityIDToLoc[cr.entityIDs[1]]

					combinedPos = pos1 + pos2

					nodes,edges = sentence.extractMinSubgraphContainingNodes(combinedPos)
					for a,b,dependencyType in edges:
						dataForThisCR[u"dependencypathelements_%s" % dependencyType] += 1
					data.append(dataForThisCR)

		return data
	
	def doDependencyPathEdgesNearEntities(self,corpus):
		entityMapping = corpus.getEntityMapping()
		data = []	
		for doc in corpus.documents:
			for sentence in doc.sentences:
				for cr,_ in sentence.candidateRelationsWithClasses:
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

	def doBigrams(self,corpus):
		entityMapping = corpus.getEntityMapping()
		data = []	
		for doc in corpus.documents:
			for sentence in doc.sentences:
				for cr,_ in sentence.candidateRelationsWithClasses:
					dataForThisCR = Counter()

					for _ in cr.entityIDs:

						startPos = 0
						endPos = len(sentence.tokens)

						tokenData = [ (sentence.tokens[i].word.lower(),sentence.tokens[i+1].word.lower()) for i in range(startPos,endPos-1) ]
						for t in tokenData:
							dataForThisCR[u"bigrams_%s_%s" % t] += 1
					data.append(dataForThisCR)

		return data

	def _vectorize(self,corpus,fit):
		assert isinstance(corpus,kindred.Corpus)
			
		matrices = []
		for feature in self.chosenFeatures:
			assert feature in self.featureInfo.keys()
			featureFunction = self.featureInfo[feature]['func']
			never_tfidf = self.featureInfo[feature]['never_tfidf']
			data = featureFunction(self,corpus)
			if fit:
				self.dictVectorizers[feature] = DictVectorizer()
				if self.tfidf and not never_tfidf:
					self.tfidfTransformers[feature] = TfidfTransformer()
					intermediate = self.dictVectorizers[feature].fit_transform(data)
					matrices.append(self.tfidfTransformers[feature].fit_transform(intermediate))
				else:
					matrices.append(self.dictVectorizers[feature].fit_transform(data))
			else:
				if self.tfidf and not never_tfidf:
					intermediate = self.dictVectorizers[feature].transform(data)
					matrices.append(self.tfidfTransformers[feature].transform(intermediate))
				else:
					matrices.append(self.dictVectorizers[feature].transform(data))

		mergedMatrix = hstack(matrices)
		return mergedMatrix
			
	def fit_transform(self,corpus):
		assert self.fitted == False
		self.fitted = True
		return self._vectorize(corpus,True)
	
	def transform(self,corpus):
		assert self.fitted == True
		return self._vectorize(corpus,False)
		
		
	
