
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from collections import defaultdict

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
import numpy as np

class RelationClassifier:
	"""
	Manages binary classifier(s) for relation classification.
	
	:param classifierType: Which classifier is used ('SVM' or 'LogisticRegression')
	:param tfidf: Whether it will use tfidf for the vectorizer
	:param features: A list of specific features. Valid features are "entityTypes", "unigramsBetweenEntities", "bigrams", "dependencyPathEdges", "dependencyPathEdgesNearEntities"
	:param threshold: A specific threshold to use for classification (which will then use a logistic regression classifier)
	:param entityCount: Number of entities in each relation (default=2). Passed to the CandidateBuilder (if needed)
	:param acceptedEntityTypes: Tuples of entity types that relations must match. None will match allow relations of any entity types. Passed to the CandidateBuilder (if needed)
	:param isTrained: Whether the classifier has been trained yet. Will throw an error if predict is called before it is trained.
	"""
	
	def __init__(self,classifierType='SVM',tfidf=True,features=None,threshold=None,entityCount=2,acceptedEntityTypes=None,model='en'):
		"""
		Constructor for the RelationClassifier class
		
		:param classifierType: Which classifier to use (must be 'SVM' or 'LogisticRegression')
		:param tfidf: Whether to use tfidf for the vectorizer
		:param features: A list of specific features. Valid features are "entityTypes", "unigramsBetweenEntities", "bigrams", "dependencyPathEdges", "dependencyPathEdgesNearEntities"
		:param threshold: A specific threshold to use for classification (which will then use a logistic regression classifier)
		:param entityCount: Number of entities in each relation (default=2). Passed to the CandidateBuilder (if needed)
		:param acceptedEntityTypes: Tuples of entity types that relations must match. None will match allow relations of any entity types. Passed to the CandidateBuilder (if needed)
		:param model: Name of an available Spacy language model for any parsing needed (e.g. en/de/es/pt/fr/it/nl)
		:type classifierType: str
		:type tfidf: bool
		:type features: list of str
		:type threshold: float
		:type entityCount: int
		:type acceptedEntityTypes: list of tuples
		:type model: str
		"""
		assert classifierType in ['SVM','LogisticRegression'], "classifierType must be 'SVM' or 'LogisticRegression'"
		assert classifierType == 'LogisticRegression' or threshold is None, "Threshold can only be used when classifierType is 'LogisticRegression'"

		assert isinstance(tfidf,bool)
		assert threshold is None or isinstance(threshold,float)
		assert isinstance(entityCount,int)
		assert acceptedEntityTypes is None or isinstance(acceptedEntityTypes,list)

		self.isTrained = False
		self.classifierType = classifierType
		self.tfidf = tfidf

		self.entityCount = entityCount
		self.acceptedEntityTypes = acceptedEntityTypes

		self.chosenFeatures = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]
		if not features is None:
			assert isinstance(features,list)
			self.chosenFeatures = features
			
		self.threshold = threshold
		self.model = model

	def train(self,corpus):
		"""
		Trains the classifier using this corpus. All relations in the corpus will be used for training.

		:param corpus: Corpus to use for training
		:type corpus: kindred.Corpus
		"""
		assert isinstance(corpus,kindred.Corpus)

		if not corpus.parsed:
			parser = kindred.Parser(model=self.model)
			parser.parse(corpus)
		
		self.candidateBuilder = CandidateBuilder(entityCount=self.entityCount,acceptedEntityTypes=self.acceptedEntityTypes)
		candidateRelations = self.candidateBuilder.build(corpus)

		if len(candidateRelations) == 0:
			raise RuntimeError("No candidate relations found in corpus for training. Does the corpus contain text and entity annotations with at least one sentence containing %d entities." % (self.entityCount))

		candidateRelationKeys = set()
		for cr in candidateRelations:
			assert isinstance(cr,kindred.CandidateRelation)
			for knownType,knownArgNames in cr.knownTypesAndArgNames:
				relKey = tuple([knownType] + knownArgNames)
				candidateRelationKeys.add(relKey)
		
		# Create mappings from the class index to a relation type and back again
		self.colToRelType = sorted(list(candidateRelationKeys))
		self.relTypeToCol = { relationType:i for i,relationType in enumerate(self.colToRelType) }
		
		Y = np.zeros((len(candidateRelations),len(self.colToRelType)),np.int32)
		
		candidateClasses = []
		for i,cr in enumerate(candidateRelations):
			for knownType,knownArgNames in cr.knownTypesAndArgNames:
				relKey = tuple([knownType] + knownArgNames)
				col = self.relTypeToCol[relKey]
				Y[i,col] = 1

		entityCountsInRelations = set([ len(r.entities) for r in corpus.getRelations() ])
		entityCountsInRelations = sorted(list(set(entityCountsInRelations)))
		assert self.entityCount in entityCountsInRelations, "Relation classifier is expecting to train on relations with %d entities (entityCount=%d). But the known relations in the corpus contain relations with the following entity counts: %s. Perhaps the entityCount parameter should be changed or there is a problem with the training corpus." % (self.entityCount,self.entityCount,str(entityCountsInRelations))

		self.relTypeToValidEntityTypes = defaultdict(set)

		for d in corpus.documents:
			for r in d.relations:
				validEntityTypes = tuple([ e.entityType for e in r.entities ])
				
				relKey = tuple([r.relationType] + r.argNames)
				self.relTypeToValidEntityTypes[relKey].add(validEntityTypes)

		self.vectorizer = Vectorizer(entityCount=self.entityCount,featureChoice=self.chosenFeatures,tfidf=self.tfidf)
		trainVectors = self.vectorizer.fit_transform(candidateRelations)
	
		assert trainVectors.shape[0] == Y.shape[0]

		posCount = Y.sum()
		negCount = Y.shape[0]*Y.shape[1] - posCount

		assert negCount > 0, "Must have at least one negative candidate relation in set for training"
		assert posCount > 0, "Must have at least one positive candidate relation in set for training"

		self.clf = None
		if self.classifierType == 'SVM':
			self.clf = kindred.MultiLabelClassifier(svm.LinearSVC,class_weight='balanced',random_state=1,max_iter=10000)
		elif self.classifierType == 'LogisticRegression' and self.threshold is None:
			self.clf = kindred.MultiLabelClassifier(LogisticRegression,class_weight='balanced',random_state=1,solver='liblinear',multi_class='ovr')
		elif self.classifierType == 'LogisticRegression' and not self.threshold is None:
			self.clf = kindred.MultiLabelClassifier(kindred.LogisticRegressionWithThreshold,threshold=self.threshold)
		
		self.clf.fit(trainVectors,Y)
		
		self.isTrained = True

	def predict(self,corpus):
		"""
		Use the relation classifier to predict new relations for a corpus. The new relations will be added to the Corpus.

		:param corpus: Corpus to make predictions on
		:type corpus: kindred.Corpus
		"""
		assert self.isTrained, "Classifier must be trained using train() before predictions can be made"
	
		assert isinstance(corpus,kindred.Corpus)
		
		if not corpus.parsed:
			parser = kindred.Parser(model=self.model)
			parser.parse(corpus)
		
		candidateRelations = self.candidateBuilder.build(corpus)

		# Check if there are any candidate relations to classify in this corpus
		if len(candidateRelations) == 0:
			return
		
		predictedRelations = []
		testVectors = self.vectorizer.transform(candidateRelations)

		classMatrix = self.clf.predict(testVectors)
		if self.clf.has_predict_proba():
			probMatrix = self.clf.predict_proba(testVectors)
		else:
			probMatrix = None


		predictedProb = None
		for matrixRow,matrixCol in zip(*classMatrix.nonzero()):
			candidateRelation = candidateRelations[matrixRow]

			if probMatrix is not None:
				predictedProb = probMatrix[matrixRow,matrixCol]

			relKey = self.colToRelType[matrixCol]
			relType = relKey[0]
			argNames = relKey[1:]
			
			candidateRelationEntityTypes = tuple( [ e.entityType for e in candidateRelation.entities ] )
			if not tuple(candidateRelationEntityTypes) in self.relTypeToValidEntityTypes[relKey]:
				continue

			predictedRelation = kindred.Relation(relType,candidateRelation.entities,argNames=argNames,probability=predictedProb)
			predictedRelations.append(predictedRelation)

		# Add the predicted relations into the corpus
		entitiesToDoc = {}
		for i,doc in enumerate(corpus.documents):
			for e in doc.entities:
				entitiesToDoc[e] = i

		for predictedRelation in predictedRelations:
			docIDs = [ entitiesToDoc[e] for e in predictedRelation.entities ]
			docIDs = list(set(docIDs))
			assert len(docIDs) > 0, "Predicted relation contains entities that don't match any documents in corpus"
			assert len(docIDs) == 1, "Predicted relation contains entities that are spread across documents"

			docID = docIDs[0]
			if not predictedRelation in corpus.documents[docID].relations:
				corpus.documents[docID].addRelation(predictedRelation)

