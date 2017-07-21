
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
		validFeatures = ["ngrams_betweenEntities"]
		if featureChoice is None:
			self.chosenFeatures = validFeatures
		else:
			for f in featureChoice:
				assert f in validFeatures, "Feature (%s) is not a valid feature" % f
			self.chosenFeatures = featureChoice
		
		self.tfidf = tfidf
		
	def getFeatureNames(self):
		assert self.fitted == True, "Must have fit data first"
		featureNames = []
		return self.dictVec_selectedtokentypes.get_feature_names()
		
	def doStuff(self,corpus,candidateRelations,fit):
		assert isinstance(corpus,kindred.Corpus)
		assert isinstance(candidateRelations,list)
		for r in candidateRelations:
			assert isinstance(r,kindred.Relation)
					
		entityMapping = corpus.getEntityMapping()
				
		lotsOData = []
		for cr in candidateRelations:
			stuff = {}
			for argI,eID in enumerate(cr.entityIDs):
				eType = entityMapping[eID].entityType
				argName = "selectedtokentypes_%d_%s" % (argI,eType)
				stuff[argName] = 1
			lotsOData.append(stuff)
			
		if fit:
			self.dictVec_selectedtokentypes = DictVectorizer()
			return self.dictVec_selectedtokentypes.fit_transform(lotsOData)
		else:
			return self.dictVec_selectedtokentypes.transform(lotsOData)
			
	def fit_transform(self,corpus,candidateRelations):
		assert self.fitted == False
		self.fitted = True
		return self.doStuff(corpus,candidateRelations,True)
	
	def fit(self,corpus,candidateRelations):
		fit_transform(self,corpus,candidateRelations)
		
	def transform(self,corpus,candidateRelations):
		assert self.fitted == True
		return self.doStuff(corpus,candidateRelations,False)
		
		
	