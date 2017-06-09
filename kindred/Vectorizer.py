
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import coo_matrix, csr_matrix, lil_matrix, hstack, vstack

import kindred
from kindred.VERSE_vectorizer import VERSEVectorizer

class Vectorizer:
	def __init__(self):
		self.dictVectorizers = {}
		self.verseVectorizer = None
		pass
		
	def corpusToVectors(self,corpus,name,doTFIDF=True):
		vectorizerName = "%s_vectorizer" %  name
		tfidfName = "%s_tfidf" % name
		
		if not vectorizerName in self.dictVectorizers:
			self.dictVectorizers[vectorizerName] = DictVectorizer()
			vecs = self.dictVectorizers[vectorizerName].fit_transform(corpus)
			if doTFIDF:
				self.dictVectorizers[tfidfName] = TfidfTransformer()
				vecs = self.dictVectorizers[tfidfName].fit_transform(vecs)
				
			return vecs
		else:
			vecs = self.dictVectorizers[vectorizerName].transform(corpus)
			if doTFIDF:
				vecs = self.dictVectorizers[tfidfName].transform(vecs)
			return vecs
		
	def doSelectedTokenTypes(self,candidateRelations,argID):
		corpus = []

		for candidate in candidateRelations:
			if argID < len(candidate.entitiesInRelation):
				entityID = candidate.entitiesInRelation[argID]
				assert entityID in candidate.processedSentence.getEntityIDs()
				entityType = candidate.processedSentence.getEntityType(entityID)
				corpus.append(Counter([entityType]))
			
		return self.corpusToVectors(corpus,'SelectedTokenTypes_'+str(argID),False)
		
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


	def transform2(self,candidateRelations):
		assert isinstance(candidateRelations,list)
		assert len(candidateRelations) > 0
		for candidateRelation in candidateRelations:
			assert isinstance(candidateRelation,kindred.CandidateRelation)
			
		if not 'maxArgCount' in self.__dict__:
			self.maxArgCount = max( [ len(candidateRelation.entitiesInRelation) for candidate in candidateRelations ] )
			
		allVecs = []
		for argID in range(self.maxArgCount):
			vecs = self.doSelectedTokenTypes(candidateRelations,argID)
			allVecs.append(vecs)
			
		combined = hstack( allVecs )
		
		return combined
		
