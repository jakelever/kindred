import sys

import kindred

from kindred.datageneration import generateData,generateTestData

def _bionlpst_bb3(swap):
	trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
	devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')

	if swap:
		trainCorpus,devCorpus = devCorpus,trainCorpus

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier(useBuilder=True)
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	scores = kindred.evaluate(devCorpus, predictionCorpus, metric='all')
	print("bb3 scores:",scores,swap)

def _bionlpst_seedev(swap):
	trainCorpus = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devCorpus = kindred.bionlpst.load('2016-SeeDev-binary-dev')
	
	if swap:
		trainCorpus,devCorpus = devCorpus,trainCorpus

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	scores = kindred.evaluate(devCorpus, predictionCorpus, metric='all')
	print("seedev scores:",scores,swap)

if __name__ == '__main__':
	_bionlpst_bb3(False)
	_bionlpst_bb3(True)
	_bionlpst_seedev(False)
	_bionlpst_seedev(True)

