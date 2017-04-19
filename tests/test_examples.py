import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

def test_bionlpst():
	trainData = kindred.BioNLPSTData('2016-BB3-event-training')
	devData = kindred.BioNLPSTData('2016-BB3-event-development')
	model = kindred.train(trainData)
	predictedRelations = model.predict(dev_data.getTextAndEntities())
	f1score = kindred.evaluate(dev_data.getRelations(), predictionRelations, metric='f1score')
	assert f1score > 0.5

def test_pubannotation():
	trainData = kindred.PubAnnotationData('2016-SeeDev-binary-training')
	model = kindred.train(trainData)
	text = 'A SeeDev related text goes here'
	predictedRelations = model.predict(text)
	assert len(predicted_relations) == 1

def test_pubtator():
	assert False
	
def test_unicodeCheck():
	assert False
	
def test_exportToST():
	assert False

def test_naryRelations():
	assert False
	
if __name__ == '__main__':
	test_simpleRelationCheck()
