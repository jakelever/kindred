import kindred
import pytest

from kindred.datageneration import generateData,generateTestData

def test_simpleRelationClassifier_binary():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0

def test_simpleRelationClassifier_triple():
	trainCorpus, testCorpusGold = generateTestData(entityCount=3,positiveCount=100,negativeCount=100)

	trainRelations = trainCorpus.getRelations()
	assert len(trainRelations) == 50
	for r in trainRelations:
		assert len(r.entities) == 3

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(entityCount=3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)

	predictedRelations = predictionCorpus.getRelations()
	assert len(predictedRelations) == 50
	for r in predictedRelations:
		assert len(r.entities) == 3
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0

def test_simpleRelationClassifier_emptyTestCorpus():
	trainCorpus, testCorpus = generateTestData(positiveCount=100,negativeCount=100)

	for doc in testCorpus.documents:
		doc.entities = []
		doc.relations = []

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(testCorpus)

	assert len(testCorpus.getRelations()) == 0

def test_simpleRelationClassifier_emptyTrainCorpus():
	trainCorpus, testCorpus = generateTestData(positiveCount=100,negativeCount=100)

	for doc in trainCorpus.documents:
		doc.entities = []
		doc.relations = []

	classifier = kindred.RelationClassifier()

	with pytest.raises(RuntimeError) as excinfo:
		classifier.train(trainCorpus)
	assert excinfo.value.args == ('No candidate relations found in corpus for training. Does the corpus contain text and entity annotations with at least one sentence containing 2 entities.',)

def _SeeDevmini():
	trainCorpus = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devCorpus = kindred.bionlpst.load('2016-SeeDev-binary-dev')

	trainCorpus.documents = trainCorpus.documents[1:2]
	devCorpus.documents = devCorpus.documents[:1]

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.235

def test_singleClassifier():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.519

def test_singleClassifier_triple():
	trainCorpus, devCorpus = generateTestData(entityCount=3,positiveCount=100,negativeCount=100,relTypes=2)

	trainRelations = trainCorpus.getRelations()
	assert len(trainRelations) == 50
	for r in trainRelations:
		assert len(r.entities) == 3

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(entityCount=3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	predictedRelations = predictionCorpus.getRelations()
	assert len(predictedRelations) == 50
	for r in predictedRelations:
		assert len(r.entities) == 3
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.54

def test_noTFIDF():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(tfidf=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.538

def test_logisticregression():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(classifierType='LogisticRegression')
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.558

def test_logisticregression_threshold():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(classifierType='LogisticRegression',threshold=0.3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.558

def test_singleFeature_entityTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(features=['entityTypes'])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.577

def test_filterByEntityTypes_validTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(features=["unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.481

def test_filterByEntityTypes_invalidTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	for doc in devCorpus.documents:
		for e in doc.entities:
			e.entityType = 'a new type'

	classifier = kindred.RelationClassifier(features=["unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.0

if __name__ == '__main__':
	test_singleFeature_entityTypes()

