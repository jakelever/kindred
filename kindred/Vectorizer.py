
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import coo_matrix, csr_matrix, lil_matrix, hstack, vstack

import kindred
from kindred.VERSE_vectorizer import VERSEVectorizer

class Vectorizer:
	"""
	Vectorizes set of candidate relations into scipy sparse matrix.
	"""
	
	def __init__(self,featureChoice=None,tfidf=True):
		self.verseVectorizer = None
		self.featureChoice = featureChoice
		self.tfidf = tfidf
		
	def getFeatureNames(self):
		assert not self.verseVectorizer is None, "Must have fit data first"
		return self.verseVectorizer.getFeatureNames()
				
	def fit_transform(self,corpus,candidateRelations):
		assert self.verseVectorizer is None, "Vectorizer has already been fit. Use transform() instead"
	
		assert isinstance(corpus,kindred.Corpus)
		assert isinstance(candidateRelations,list)
		for r in candidateRelations:
			assert isinstance(r,kindred.Relation)
			
		self.verseVectorizer = VERSEVectorizer(corpus,candidateRelations,self.featureChoice,self.tfidf)
		return self.verseVectorizer.getTrainingVectors()
		
	def fit(self,corpus,candidateRelations):
		self.fit_transform(self,corpus,candidateRelations)
		
	def transform(self,corpus,candidateRelations):
		assert not self.verseVectorizer is None, "Vectorizer has not been fit. Use fit() or fit_transform() first"
		
		assert isinstance(corpus,kindred.Corpus)
		assert isinstance(candidateRelations,list)
		for r in candidateRelations:
			assert isinstance(r,kindred.Relation)
		
		return self.verseVectorizer.vectorize(corpus,candidateRelations)
		



class Vectorizer2:
	"""
	Vectorizes set of candidate relations into scipy sparse matrix.
	"""
	
	def __init__(self,featureChoice=None,tfidf=True):
		self.fitted = False
		
		validFeatures = ["selectedTokenTypes"]
		#validFeatures = ["ngrams_betweenEntities"]
		if featureChoice is None:
			self.chosenFeatures = validFeatures
		else:
			for f in featureChoice:
				assert f in validFeatures, "Feature (%s) is not a valid feature" % f
			self.chosenFeatures = featureChoice
		
		self.tfidf = tfidf

		self._registerFunctions()
		self.dictVectorizers = {}

	def _registerFunctions(self):
		self.funcCalls = {}
		self.funcCalls['selectedTokenTypes'] = Vectorizer.doSelectedTokenTypes
		
	def getFeatureNames(self):
		assert self.fitted == True, "Must have fit data first"
		featureNames = []
		for feature in self.chosenFeatures:
			featureNames += self.dictVectorizers[feature].get_feature_names()
		return featureNames
		

	def doSelectedTokenTypes(self,corpus,candidateRelations):
		entityMapping = corpus.getEntityMapping()
		data = []	
		for cr in candidateRelations:
			stuff = {}
			for argI,eID in enumerate(cr.entityIDs):
				eType = entityMapping[eID].entityType
				argName = "selectedtokentypes_%d_%s" % (argI,eType)
				stuff[argName] = 1
			data.append(stuff)
		return data

	def _vectorize(self,corpus,candidateRelations,fit):
		assert isinstance(corpus,kindred.Corpus)
		assert isinstance(candidateRelations,list)
		for r in candidateRelations:
			assert isinstance(r,kindred.Relation)
			
		matrices = []
		for feature in self.chosenFeatures:
			assert feature in self.funcCalls
			featureFunction = self.funcCalls[feature]
			data = featureFunction(self,corpus,candidateRelations)
			if fit:
				self.dictVectorizers[feature] = DictVectorizer()
				matrices.append(self.dictVectorizers[feature].fit_transform(data))
			else:
				matrices.append(self.dictVectorizers[feature].transform(data))

		mergedMatrix = hstack(matrices)
		return mergedMatrix
			
	def fit_transform(self,corpus,candidateRelations):
		assert self.fitted == False
		self.fitted = True
		return self._vectorize(corpus,candidateRelations,True)
	
	def fit(self,corpus,candidateRelations):
		fit_transform(self,corpus,candidateRelations)
		
	def transform(self,corpus,candidateRelations):
		assert self.fitted == True
		return self._vectorize(corpus,candidateRelations,False)
		
		
	
