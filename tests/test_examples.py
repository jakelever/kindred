import sys

import kindred

from kindred.datageneration import generateData,generateTestData

def _bionlpst_bb3():
	trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
	devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	print("f1score:",f1score)
	#assert f1score > 0.5

def _bionlpst_seedev():
	trainCorpus = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devCorpus = kindred.bionlpst.load('2016-SeeDev-binary-dev')
	
	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	print("f1score:",f1score)
	#assert f1score > 0.33

if __name__ == '__main__':
	_bionlpst_bb3()
	_bionlpst_seedev()
