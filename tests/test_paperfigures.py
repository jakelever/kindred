import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

def test_bionlpst_bb3():	
	trainData = kindred.BioNLPSTData('2016-BB3-event-training_and_development')
	testData = kindred.BioNLPSTData('2016-BB3-event-test')
	
	classifier = RelationClassifier()
	classifier.train(trainData)
	
	predictedRelations = classifier.predict(testData)
	
	print(classifier.getCrossvalidatedScore())
	kindred.saveST('BB3-predictions/',testData,predictedRelations)
	
def test_bionlpst_seedev():	
	trainData = kindred.BioNLPSTData('2016-SeeDev-binary-training_and_development')
	testData = kindred.BioNLPSTData('2016-SeeDev-binary-test')
	
	classifier = RelationClassifier()
	classifier.train(trainData)
	
	predictedRelations = classifier.predict(testData)
	
	print(classifier.getCrossvalidatedScore())
	kindred.saveST('BB3-predictions/',testData,predictedRelations)
	
def test_nary():	
	trainData = kindred.BioNLPSTData('2016-SeeDev-binary-training_and_development')
	testData = kindred.BioNLPSTData('2016-SeeDev-binary-test')
	
	classifier_merge = RelationClassifier(naryMethod='merge')
	classifier_merge.train(trainData)
	predictedRelations_merge = classifier_merge.predict(testData)
	kindred.saveST('BB3-predictions-merge/',testData,predictedRelations_merge)
	
	classifier_combined = RelationClassifier(naryMethod='combine')
	classifier_combined.train(trainData)
	predictedRelations_combined = classifier_combined.predict(testData)
	kindred.saveST('BB3-predictions-combined/',testData,predictedRelations_combined)
	
def test_parser():	
	trainData = kindred.BioNLPSTData('2016-SeeDev-binary-training_and_development')
	testData = kindred.BioNLPSTData('2016-SeeDev-binary-test')
	
	classifier_stanford = RelationClassifier(parser='stanford')
	classifier_stanford.train(trainData)
	predictedRelations_stanford = classifier_stanford.predict(testData)
	kindred.saveST('BB3-predictions-stanford/',testData,predictedRelations_stanford)
	
	classifier_malt = RelationClassifier(parser='malt')
	classifier_malt.train(trainData)
	predictedRelations_malt = classifier_malt.predict(testData)
	kindred.saveST('BB3-predictions-malt/',testData,predictedRelations_malt)
	
