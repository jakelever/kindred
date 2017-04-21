
from sklearn import svm
import numpy as np

from sklearn.feature_selection import SelectKBest,chi2,SelectPercentile,RFECV
from sklearn.metrics import f1_score,confusion_matrix
from sklearn.ensemble import AdaBoostClassifier,GradientBoostingClassifier,BaggingClassifier,RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import cross_val_score,cross_val_predict,StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC,SVC

from scipy.sparse import coo_matrix, csr_matrix, lil_matrix, hstack, vstack

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer



def save_sparse_csr(filename,array):
	np.savez(filename,data = array.data ,indices=array.indices,indptr =array.indptr, shape=array.shape )

def load_sparse_csr(filename):
	loader = np.load(filename)
	return csr_matrix((  loader['data'], loader['indices'], loader['indptr']),shape = loader['shape'])

def saveClasses(filename,classes):
	with open(filename,'w') as f:
		for c in classes:
			f.write("1\n" if c == True else "0\n")

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
		
		allClasses = set()
		for c in candidateClasses:
			allClasses.update(c)
		allClasses = sorted(list(allClasses))
		allClasses = [ c for c in allClasses if c != 0 ]
		
		self.allClasses = allClasses
	
		#options = ["ngrams","selectedngrams","bigrams","ngramsPOS","selectedngramsPOS","ngramsOfDependencyPath","bigramsOfDependencyPath","selectedTokenTypes","lemmas","selectedlemmas","dependencyPathElements","dependencyPathNearSelected","splitAcrossSentences","skipgrams_2","skipgrams_3","skipgrams_4","skipgrams_5","skipgrams_6","skipgrams_7","skipgrams_8","skipgrams_9","skipgrams_10","ngrams_betweenEntities","bigrams_betweenEntities"]

		# We'll just get the vectors for the selectedTokenTypes

		tmpClassData = [ (1 in candidateClassGroup) for candidateClassGroup in candidateClasses ]

		vectorizers = {}
		trainVectors = {}

		featureChoice = ["selectedTokenTypes","dependencyPathElements","ngrams_betweenEntities","bigrams_betweenEntities","bigramsOfDependencyPath"]
		for feature in featureChoice:
			vectorizers[feature] = Vectorizer()
			trainVectors[feature] = vectorizers[feature].transform(candidateRelations,[feature])

		groupVector = None
		chosenFeatures = []
		prevScore,prevMatrix = -1.0, None
		while True:
			bestScore, bestFeature, bestMatrix = -1.0, None, None
			for feature in featureChoice:
				if prevMatrix is None:
					matrix = trainVectors[feature]
				else:
					matrix = hstack([prevMatrix,trainVectors[feature]])

				clf = svm.LinearSVC(class_weight='balanced')
				
				scores = cross_val_score(clf, matrix, tmpClassData, cv=5, scoring='f1_macro')
				score = scores.mean()

				print chosenFeatures, feature, score, scores
				if score > bestScore:
					bestScore = score
					bestFeature = feature
					bestMatrix = matrix

			if bestScore > prevScore:
				# We see improvement
				featureChoice.remove(bestFeature)
				chosenFeatures.append(bestFeature)
				prevScore = bestScore
				prevMatrix = bestMatrix
			else:
				# No improvement made
				break
				
		print chosenFeatures
		#assert False
		self.vectorizer = Vectorizer()
		trainVectors = self.vectorizer.transform(candidateRelations,featureChoice=chosenFeatures)
	
		print trainVectors.shape
		assert trainVectors.shape[0] == len(candidateClasses)
		
		
		# TODO: Should we take into account the argument count when grouping classifiers?
		self.clfs = {}
		for c in self.allClasses:
			tmpClassData = [ (c in candidateClassGroup) for candidateClassGroup in candidateClasses ]

			save_sparse_csr('train.matrix',trainVectors.tocsr())
			saveClasses('train.classes',tmpClassData)

			self.clfs[c] = svm.LinearSVC(class_weight='balanced')
			#self.clfs[c] = AdaBoostClassifier(n_estimators=2)
			self.clfs[c].fit(trainVectors,tmpClassData)
		
		self.isTrained = True

	def predict(self,data):
		assert self.isTrained, "Classifier must be trained using train() before predictions can be made"
	
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.TextAndEntityData) or isinstance(d,kindred.RelationData)
			
		_,candidateRelations,testClasses = self.candidateBuilder.build(data)
		
		testVectors = self.vectorizer.transform(candidateRelations)

		save_sparse_csr('test.matrix',testVectors.tocsr())

		tmpClassData = [ (1 in candidateClassGroup) for candidateClassGroup in testClasses ]
		saveClasses('test.classes',tmpClassData)
		
		print testVectors.shape
		
		predictedRelations = []
		
		for c in self.allClasses:
			predictedClasses = self.clfs[c].predict(testVectors)
			for predictedClass,candidateRelation in zip(predictedClasses,candidateRelations):
				if predictedClass != 0:
					relType,nary = self.classToRelType[predictedClass]
					predictedRelation = kindred.Relation(relType,list(candidateRelation.entitiesInRelation))
					predictedRelations.append(predictedRelation)
					
		return predictedRelations
					
					
					
