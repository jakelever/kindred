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

if __name__ == '__main__':
	test_simpleRelationClassifier()

