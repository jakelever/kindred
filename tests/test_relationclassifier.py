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

def test_singleClassifier():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

def test_singleClassifier_triple():
	trainCorpus, devCorpus = generateTestData(entityCount=3,positiveCount=100,negativeCount=100,relTypes=1)

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
	assert round(f1score,3) == 1.0

def test_noTFIDF():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(tfidf=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

def test_logisticregression():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(classifierType='LogisticRegression')
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

def test_logisticregression_threshold():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(classifierType='LogisticRegression',threshold=0.3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

def test_singleFeature_entityTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(features=['entityTypes'])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

def test_filterByEntityTypes_validTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(features=["unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.97

def test_filterByEntityTypes_invalidTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

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

def test_predicting_thrice():
	trainCorpus1, trainCorpus2 = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)
	trainCorpus3, testCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	for doc in trainCorpus1.documents:
		for r in doc.relations:
			r.relationType = 'type1'
	for doc in trainCorpus2.documents:
		for r in doc.relations:
			r.relationType = 'type2'
	for doc in trainCorpus3.documents:
		for r in doc.relations:
			r.relationType = 'type3'

	testCorpus.removeRelations()

	classifier1 = kindred.RelationClassifier()
	classifier1.train(trainCorpus1)
	classifier2 = kindred.RelationClassifier()
	classifier2.train(trainCorpus2)
	classifier3 = kindred.RelationClassifier()
	classifier3.train(trainCorpus3)

	classifier1.predict(testCorpus)
	classifier2.predict(testCorpus)
	classifier3.predict(testCorpus)

	relations = [ r for doc in testCorpus.documents for r in doc.relations ]
	assert len(relations) == len(set(relations)), "Duplicate relations found in predictions"

def test_predicting_duplicates():
	trainCorpus, testCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	testCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)

	classifier.predict(testCorpus)
	classifier.predict(testCorpus)
	classifier.predict(testCorpus)

	relations = [ r for doc in testCorpus.documents for r in doc.relations ]
	assert len(relations) == len(set(relations)), "Duplicate relations found in predictions"
			
def test_singleClassifier_twoRelTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.687

def test_doublelabels():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=1)

	for doc in trainCorpus.documents:
		newRelations = [ kindred.Relation("anotherLabel",r.entities,r.argNames) for r in doc.relations ]
		doc.relations += newRelations
	for doc in devCorpus.documents:
		newRelations = [ kindred.Relation("anotherLabel",r.entities,r.argNames) for r in doc.relations ]
		doc.relations += newRelations

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 1.0

if __name__ == '__main__':
	test_singleFeature_entityTypes()

