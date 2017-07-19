
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
	
	def __init__(self):
		self.verseVectorizer = None
		
	def getFeatureNames(self):
		assert not self.verseVectorizer is None, "Must have fit data first"
		return self.verseVectorizer.getFeatureNames()
		
	def transform(self,corpus,candidateRelations,featureChoice=None,tfidf=None):
		assert isinstance(corpus,kindred.Corpus)
		assert isinstance(candidateRelations,list)
		for r in candidateRelations:
			assert isinstance(r,kindred.Relation)
		
		if self.verseVectorizer is None:
			self.verseVectorizer = VERSEVectorizer(corpus,candidateRelations,featureChoice,tfidf)
			return self.verseVectorizer.getTrainingVectors()
		else:
			return self.verseVectorizer.vectorize(corpus,candidateRelations)


