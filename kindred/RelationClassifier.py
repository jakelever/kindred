
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from collections import defaultdict

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

class RelationClassifier:
	"""
	Manages binary classifier(s) for relation classification.
	"""
	def __init__(self,classifierType='SVM',tfidf=True,features=None,threshold=None):
		"""
		Constructor for the RelationClassifier class
		
		:param classifierType: Which classifier to use (must be 'SVM' or 'LogisticRegression')
		:param tfidf: Whether to use tfidf for the vectorizer
		:param features: A list of specific features. Valid features are "entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"
		:param threshold: A specific threshold to use for classification (which will then use a logistic regression classifier)
		:type classifierType: str
		:type tfidf: bool
		:type features: list of str
		:type threshold: float
		"""
		assert classifierType in ['SVM','LogisticRegression'], "classifierType must be 'SVM' or 'LogisticRegression'"
		assert classifierType == 'LogisticRegression' or threshold is None, "Threshold can only be used when classifierType is 'LogisticRegression'"

		self.isTrained = False
		self.classifierType = classifierType
		self.tfidf = tfidf

		self.chosenFeatures = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]
		if not features is None:
			assert isinstance(features,list)
			self.chosenFeatures = features
			
		self.threshold = threshold

	def train(self,corpus):
		"""
		Trains the classifier using this corpus. All relations in the corpus will be used for training.

		:param corpus: Corpus to use for training
		:type corpus: kindred.Corpus
		"""
		assert isinstance(corpus,kindred.Corpus)
			
		self.candidateBuilder = CandidateBuilder()
		self.candidateBuilder.fit_transform(corpus)
		
		candidateRelations = corpus.getCandidateRelations()
		candidateClasses = corpus.getCandidateClasses()
		
		if len(candidateRelations) == 0:
			raise RuntimeError("No candidate relations found in corpus for training")

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
	
		simplifiedClasses = []
		# TODO: Try sparse matrix rep
		for candidateRelation,candidateClassGroup in zip(candidateRelations,candidateClasses):
			simplifiedClasses.append(candidateClassGroup[0])

		self.vectorizer = Vectorizer(featureChoice=self.chosenFeatures,tfidf=self.tfidf)
		trainVectors = self.vectorizer.fit_transform(corpus)
	
		assert trainVectors.shape[0] == len(candidateClasses)

		self.clf = None
		if self.classifierType == 'SVM':
			self.clf = svm.LinearSVC(class_weight='balanced',random_state=1)
		elif self.classifierType == 'LogisticRegression' and self.threshold is None:
			self.clf = LogisticRegression(class_weight='balanced',random_state=1)
		elif self.classifierType == 'LogisticRegression' and not self.threshold is None:
			self.clf = kindred.LogisticRegressionWithThreshold(self.threshold)

		self.clf.fit(trainVectors,simplifiedClasses)
		
		self.isTrained = True

	def predict(self,corpus):
		"""
		Use the relation classifier to predict new relations for a corpus. The new relations will be added to the Corpus.

		:param corpus: Corpus to make predictions on
		:type corpus: kindred.Corpus
		"""
		assert self.isTrained, "Classifier must be trained using train() before predictions can be made"
	
		assert isinstance(corpus,kindred.Corpus)
			
		self.candidateBuilder.transform(corpus)

		candidateRelations = corpus.getCandidateRelations()

		# Check if there are any candidate relations to classify in this corpus
		if len(candidateRelations) == 0:
			return
		
		entityIDsToType = {}
		for doc in corpus.documents:
			for e in doc.getEntities():
				entityIDsToType[e.entityID] = e.entityType
		
		predictedRelations = []
		tmpMatrix = self.vectorizer.transform(corpus)

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

