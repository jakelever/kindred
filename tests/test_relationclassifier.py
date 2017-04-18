import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from datageneration import *

def test_simpleRelationClassifier():
	trainData, testData = generateTestData(positiveCount=5,negativeCount=5)
	
	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]
	
	classifier = RelationClassifier()
	classifier.train(trainData)
	
	predictedRelations = classifier.predict(testData_TextAndEntities)
	
	evaluator = Evaluator()
	f1score = evaluator.evaluate(testData_Relations, predictedRelations, metric='f1score')
	assert f1score == 1.0
