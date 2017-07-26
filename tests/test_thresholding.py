import kindred

from kindred.datageneration import generateData,generateTestData

def _featureBuilding(useBB3):
	#trainData, testData = generateTestData(positiveCount=100,negativeCount=100)
	
	if useBB3:
		trainData = kindred.bionlpst.load('2016-BB3-event-train')
		testData = kindred.bionlpst.load('2016-BB3-event-dev')
		chosenFeatures = ["entityTypes","unigramsBetweenEntities"]
	else:
		trainData = kindred.bionlpst.load('2016-SeeDev-binary-train')
		testData = kindred.bionlpst.load('2016-SeeDev-binary-dev')
		chosenFeatures = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]

	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]




	finalChosenFeatures = []

	for threshold in range(1,100,2):
		fthreshold = threshold/float(100)
		classifier = kindred.RelationClassifier(useBuilder=False,features=chosenFeatures,threshold=fthreshold)
		classifier.train(trainData)
	
		predictedRelations = classifier.predict(testData_TextAndEntities)
	
		evaluator = Evaluator()
		precision,recall,f1score = evaluator.evaluate(testData_Relations, predictedRelations, metric='all', display=False)
		print(fthreshold,precision,recall,f1score)

if __name__ == '__main__':
	print("BB3")
	_featureBuilding(True)
	print("SeeDev")
	_featureBuilding(False)


