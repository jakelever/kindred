import kindred
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

def test_simpleRelationClassifier():
	trainData, testData = generateTestData(positiveCount=100,negativeCount=100)
	
	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]
	
	classifier = RelationClassifier()
	classifier.train(trainData)
	
	print testData_Relations
	predictedRelations = classifier.predict(testData_TextAndEntities)
	print predictedRelations
	
	evaluator = Evaluator()
	f1score = evaluator.evaluate(testData_Relations, predictedRelations, metric='f1score')
	assert f1score == 1.0

if __name__ == '__main__':
	test_simpleRelationClassifier()

