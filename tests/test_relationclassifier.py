import kindred
from kindred.RelationClassifier import RelationClassifier

from kindred.datageneration import generateData,generateTestData

def test_simpleRelationClassifier():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0

def test_simpleMultiClassRelationClassifier():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(useSingleClassifier=False)
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

	classifier = RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.235

def test_singleClassifier():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.458

def test_multiClassifiers():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(useSingleClassifier=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.646

def test_featureBuilder():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(useBuilder=True)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.604

def test_multiClassifiersAndFeatureBuilder():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(useSingleClassifier=False,useBuilder=True)
	classifier.train(trainCorpus)

	classifier.predict(predictionCorpus)

	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.646

def test_noTFIDF():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(tfidf=False)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.438

def test_threshold():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(threshold=0.3)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.583

def test_singleFeature_selectionTokenTypes():
	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = RelationClassifier(features=['selectedTokenTypes'])
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.354

if __name__ == '__main__':
	test_singleFeature_selectionTokenTypes()

