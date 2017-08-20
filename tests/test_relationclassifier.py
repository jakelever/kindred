import kindred

from kindred.datageneration import generateData,generateTestData

def test_simpleRelationClassifier():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0

def test_simpleMultiClassRelationClassifier():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useSingleClassifier=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0

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
	assert round(f1score,3) == 0.538

def test_multiClassifiers():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useSingleClassifier=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.423

def test_multiClassifiers_threshold():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useSingleClassifier=False,threshold=0.9)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.176

def test_featureBuilder():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useBuilder=True)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.481

def test_multiClassifiersAndFeatureBuilder():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useSingleClassifier=False,useBuilder=True)
	classifier.train(trainCorpus)

	classifier.predict(predictionCorpus)

	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.423

def test_noTFIDF():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(tfidf=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.558

def test_threshold():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(threshold=0.3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.519

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
	assert round(f1score,3) == 0.5

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

def test_filterByEntityTypes_validTypes_multi():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useSingleClassifier=False, features=["unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.423

def test_filterByEntityTypes_invalidTypes_multi():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	for doc in devCorpus.documents:
		for e in doc.entities:
			e.entityType = 'a new type'

	classifier = kindred.RelationClassifier(useSingleClassifier=False, features=["unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.0

if __name__ == '__main__':
	test_singleFeature_entityTypes()

