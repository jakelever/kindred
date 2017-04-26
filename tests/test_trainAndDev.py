import sys

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

def _bionlpst_bb3(swap):
	trainData = kindred.bionlpst.load('2016-BB3-event-train')
	devData = kindred.bionlpst.load('2016-BB3-event-dev')

	if swap:
		trainData,devData = devData,trainData
	
	devData_TextAndEntities = [ d.getTextAndEntities() for d in devData ]
	devData_Relations = [ d.getRelations() for d in devData ]

	classifier = RelationClassifier(useBuilder=True)
	classifier.train(trainData)
	predictedRelations = classifier.predict(devData) #devData_TextAndEntities)
	evaluator = Evaluator()
	scores = evaluator.evaluate(devData_Relations, predictedRelations, metric='all')
	print("bb3 scores:",scores,swap)

def _bionlpst_seedev(swap):
	trainData = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devData = kindred.bionlpst.load('2016-SeeDev-binary-dev')
	
	if swap:
		trainData,devData = devData,trainData

	devData_TextAndEntities = [ d.getTextAndEntities() for d in devData ]
	devData_Relations = [ d.getRelations() for d in devData ]

	classifier = RelationClassifier()
	classifier.train(trainData)

	predictedRelations = classifier.predict(devData) #devData_TextAndEntities)

	evaluator = Evaluator()
	scores = evaluator.evaluate(devData_Relations, predictedRelations, metric='all')
	print("seedev scores:",scores,swap)

if __name__ == '__main__':
	_bionlpst_bb3(False)
	_bionlpst_bb3(True)
	_bionlpst_seedev(False)
	_bionlpst_seedev(True)

