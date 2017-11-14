import kindred
import pytest
import pickle
import tempfile

from kindred.datageneration import generateData,generateTestData

def test_pickle():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)

	predictionCorpus = testCorpusGold.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)

	with tempfile.NamedTemporaryFile() as tempF:
		with open(tempF.name,'wb') as f:
			pickle.dump(classifier,f)
		with open(tempF.name,'rb') as f:
			classifier = pickle.load(f)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(testCorpusGold, predictionCorpus, metric='f1score')
	assert f1score == 1.0
