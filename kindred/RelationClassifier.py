
from sklearn import svm
import numpy as np

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

class RelationClassifier:
	"""
	This is a class. Fantastic!
	"""
	def __init__(self):
		"""
		Constructor-time
		"""
		self.isTrained = False

	def train(self,data):
		"""
		Does stuff
		"""
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.RelationData)
			
		self.candidateBuilder = CandidateBuilder()
		relTypes,candidateRelations,candidateClasses = self.candidateBuilder.build(data)
				
		self.classToRelType = { (i+1):relType for i,relType in enumerate(relTypes) }
		
		# We'll just get the vectors for the selectedTokenTypes
		self.vectorizer = Vectorizer()
		trainVectors = self.vectorizer.transform(candidateRelations)
		
		assert trainVectors.shape[0] == len(candidateClasses)
		
		allClasses = set()
		for c in candidateClasses:
			allClasses.update(c)
		allClasses = sorted(list(allClasses))
		allClasses = [ c for c in allClasses if c != 0 ]
		
		self.allClasses = allClasses
		print allClasses
		
		# TODO: Should we take into account the argument count when grouping classifiers?
		self.clfs = {}
		for c in self.allClasses:
			tmpClassData = [ (c in candidateClassGroup) for candidateClassGroup in candidateClasses ]
			self.clfs[c] = svm.LinearSVC(class_weight='balanced')
			self.clfs[c].fit(trainVectors,tmpClassData)
		
		self.isTrained = True

	def predict(self,data):
		assert self.isTrained, "Classifier must be trained using train() before predictions can be made"
	
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.TextAndEntityData)
			
		_,candidateRelations,_ = self.candidateBuilder.build(data)
		
		testVectors = self.vectorizer.transform(candidateRelations)
		
		predictedRelations = []
		
		for c in self.allClasses:
			predictedClasses = self.clfs[c].predict(testVectors)
			#print predictedClasses
			for predictedClass,candidateRelation in zip(predictedClasses,candidateRelations):
				if predictedClass != 0:
					relType,nary = self.classToRelType[predictedClass]
					predictedRelation = tuple([relType] + list(candidateRelation.entitiesInRelation))
					predictedRelations.append(predictedRelation)
					
		return predictedRelations
					
					
					
