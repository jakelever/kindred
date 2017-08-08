
from sklearn import svm
from collections import defaultdict

from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

class RelationClassifier:
	"""
	Manages binary classifier(s) for relation classification.
	"""
	def __init__(self,useSingleClassifier=True,useBuilder=False,tfidf=True,features=None,threshold=None):
		"""
		Constructor for the RelationClassifier class
		
		:param self: Object instance
		:param useSingleClassifier: Whether to use a single classifier
		:param useBuilder: Whether to use the feature builder functionality
		:param tfidf: Whether to use tfidf for the vectorizer
		:param features: A list of specific features
		:param threshold: A specific threshold to use for classification (which will then use a logistic regression classifier)
		"""
		self.isTrained = False
		self.useSingleClassifier = useSingleClassifier
		self.useBuilder = useBuilder
		self.tfidf = tfidf

		self.defaultFeatures = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]
		if not features is None:
			assert isinstance(features,list)
			self.defaultFeatures = features
			
		self.threshold = threshold
		#self.defaultFeatures = ["entityTypes","dependencyPathEdges"]

	def buildFeatureSet(self,corpus,candidateRelations,classes,tfidf):
		"""
		Builds the set of features that gives best cross-validated F1-score
		
		:param self: Object instance
		:param corpus: Corpus of documents to use for training
		:param candidateRelations: List of candidate relations to use for training
		:param classes: Associated numerical classes for training
		:param tfidf: Whether to use tfidf for the vectorizer
		:returns: A list of features to use for vectorizer
		"""
		
		vectorizers = {}
		trainVectors = {}

		featureChoice = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]
		for feature in featureChoice:
			vectorizers[feature] = Vectorizer(featureChoice=[feature],tfidf=tfidf)
			trainVectors[feature] = vectorizers[feature].fit_transform(corpus)

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
				
				scores = cross_val_score(clf, matrix, classes, cv=5, scoring='f1_macro')
				score = scores.mean()

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

		return chosenFeatures

	def train(self,corpus):
		"""
		Does stuff
		"""
		assert isinstance(corpus,kindred.Corpus)
			
		self.candidateBuilder = CandidateBuilder()
		self.candidateBuilder.fit_transform(corpus)
		
		self.relTypeToValidEntityTypes = defaultdict(set)
		
		for d in corpus.documents:
			for r in d.getRelations():
				entityIDsToEntities = d.getEntityIDsToEntities()
				relationEntities = [ entityIDsToEntities[eID] for eID in r.entityIDs ]
				validEntityTypes = tuple([ e.entityType for e in relationEntities ])
				
				relKey = tuple([r.relationType] + r.argNames)
				self.relTypeToValidEntityTypes[relKey].add(validEntityTypes)
			
				
		self.classToRelType = { (i+1):relType for i,relType in enumerate(corpus.relationTypes) }

		# Get the set of valid classes
		relationtypeCount = len(corpus.relationTypes)
		allClasses = list(range(1,relationtypeCount+1))
		self.allClasses = allClasses
	
		#options = ["ngrams","selectedngrams","bigrams","ngramsPOS","selectedngramsPOS","ngramsOfDependencyPath","bigramsOfDependencyPath","entityTypes","lemmas","selectedlemmas","dependencyPathEdges","dependencyPathEdgesNearEntities","splitAcrossSentences","skipgrams_2","skipgrams_3","skipgrams_4","skipgrams_5","skipgrams_6","skipgrams_7","skipgrams_8","skipgrams_9","skipgrams_10","unigramsBetweenEntities","bigrams_betweenEntities"]

		# We'll just get the vectors for the entityTypes

		#tmpClassData = [ (1 in candidateClassGroup) for candidateClassGroup in candidateClasses ]

		candidateRelations = corpus.getCandidateRelations()
		candidateClasses = corpus.getCandidateClasses()

		#useSingleClassifier = False
		if self.useSingleClassifier:
			#chosenFeatures = ["entityTypes","dependencyPathEdges","unigramsBetweenEntities","bigrams_betweenEntities","bigramsOfDependencyPath"]

			simplifiedClasses = []
			# TODO: Try sparse matrix rep
			for candidateRelation,candidateClassGroup in zip(candidateRelations,candidateClasses):
				#assert len(candidateClassGroup) == 1, "Cannot handle multiple relations with same set of entities " + str(candidateRelation)
				simplifiedClasses.append(candidateClassGroup[0])
			#assert False
	
			if self.useBuilder:
				chosenFeatures = self.buildFeatureSet(corpus,candidateRelations,simplifiedClasses,self.tfidf)
			else:
				chosenFeatures = self.defaultFeatures

			self.vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=self.tfidf)
			trainVectors = self.vectorizer.fit_transform(corpus)
		
			assert trainVectors.shape[0] == len(candidateClasses)
		
			if self.threshold is None:
				self.clf = svm.LinearSVC(class_weight='balanced',random_state=1)
			else:
				self.clf = kindred.LogisticRegressionWithThreshold(self.threshold)
			self.clf.fit(trainVectors,simplifiedClasses)
		else:
			# TODO: Should we take into account the argument count when grouping classifiers?

			if not self.useBuilder:
				chosenFeatures = self.defaultFeatures

				self.vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=self.tfidf)
				tmpMatrix = self.vectorizer.fit_transform(corpus)
			self.clfs = {}
			self.vectorizers = {}
			for c in self.allClasses:
				tmpClassData = [ (c in candidateClassGroup) for candidateClassGroup in candidateClasses ]

				if self.useBuilder:
					chosenFeatures = self.buildFeatureSet(corpus,candidateRelations,tmpClassData,self.tfidf)
					self.vectorizers[c] = Vectorizer(featureChoice=chosenFeatures,tfidf=self.tfidf)
					tmpMatrix = self.vectorizers[c].fit_transform(corpus)

				#save_sparse_csr('train.matrix',trainVectors.tocsr())
				#saveClasses('train.classes',tmpClassData)

				if self.threshold is None:
					self.clfs[c] = svm.LinearSVC(class_weight='balanced',random_state=1)
				else:
					self.clfs[c] = kindred.LogisticRegressionWithThreshold(self.threshold)
				#self.clfs[c] = AdaBoostClassifier(n_estimators=2)
				#self.clfs[c].fit(trainVectors,tmpClassData)
				self.clfs[c].fit(tmpMatrix,tmpClassData)
		
		self.isTrained = True

	def predict(self,corpus):
		assert self.isTrained, "Classifier must be trained using train() before predictions can be made"
	
		assert isinstance(corpus,kindred.Corpus)
			
		self.candidateBuilder.transform(corpus)

		#if False:
		#	testVectors = self.vectorizer.transform(candidateRelations)
		#	tmpClassData = [ (1 in candidateClassGroup) for candidateClassGroup in testClasses ]
		
		
		#save_sparse_csr('test.matrix',testVectors.tocsr())
		#saveClasses('test.classes',tmpClassData)

		candidateRelations = corpus.getCandidateRelations()
		
		entityIDsToType = {}
		for doc in corpus.documents:
			for e in doc.getEntities():
				entityIDsToType[e.entityID] = e.entityType
		
		predictedRelations = []
		
		if self.useSingleClassifier:
			tmpMatrix = self.vectorizer.transform(corpus)

			#predictedClasses = self.clfs[c].predict(testVectors)
			predictedClasses = self.clf.predict(tmpMatrix)
			for predictedClass,candidateRelation in zip(predictedClasses,candidateRelations):
				if predictedClass != 0:
					relKey = self.classToRelType[predictedClass]
					relType = relKey[0]
					argNames = relKey[1:]
					
					candidateRelationEntityTypes = tuple( [ entityIDsToType[eID] for eID in candidateRelation.entityIDs ] )
					if not tuple(candidateRelationEntityTypes) in self.relTypeToValidEntityTypes[relKey]:
						continue

					predictedRelation = kindred.Relation(relType,candidateRelation.entityIDs,argNames=argNames)
					predictedRelations.append(predictedRelation)
		else:
			if not self.useBuilder:
				tmpMatrix = self.vectorizer.transform(corpus)

			for c in self.allClasses:

				if self.useBuilder:
					tmpMatrix = self.vectorizers[c].transform(corpus)

				#predictedClasses = self.clfs[c].predict(testVectors)
				predicted = self.clfs[c].predict(tmpMatrix)
				for p,candidateRelation in zip(predicted,candidateRelations):
					if p != 0:
						relKey = self.classToRelType[p]
						relType = relKey[0]
						argNames = relKey[1:]
						
						candidateRelationEntityTypes = tuple( [ entityIDsToType[eID] for eID in candidateRelation.entityIDs ] )
						if not tuple(candidateRelationEntityTypes) in self.relTypeToValidEntityTypes[relKey]:
							continue
						
						predictedRelation = kindred.Relation(relType,candidateRelation.entityIDs,argNames=argNames)
						predictedRelations.append(predictedRelation)
		
		# Add the predicted relations into the corpus
		entitiesToDoc = {}
		for i,doc in enumerate(corpus.documents):
			for e in doc.getEntities():
				entitiesToDoc[e.entityID] = i

		for predictedRelation in predictedRelations:
			docIDs = [ entitiesToDoc[eID] for eID in predictedRelation.entityIDs ]
			docIDs = list(set(docIDs))
			assert len(docIDs) > 0, "Predicted relation contains entities that don't match any documents in corpus"
			assert len(docIDs) == 1, "Predicted relation contains entities that are spread across documents"

			docID = docIDs[0]
			corpus.documents[docID].addRelation(predictedRelation)

