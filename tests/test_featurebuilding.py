import kindred

from kindred.datageneration import generateData,generateTestData

def _featureBuilding(useBB3):
	#trainData, testData = generateTestData(positiveCount=100,negativeCount=100)
	
	if useBB3:
		trainData = kindred.bionlpst.load('2016-BB3-event-train')
		testData = kindred.bionlpst.load('2016-BB3-event-dev')
		useBuilder = True
	else:
		trainData = kindred.bionlpst.load('2016-SeeDev-binary-train')
		testData = kindred.bionlpst.load('2016-SeeDev-binary-dev')
		useBuilder = False

	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]

	featureChoice = ["entityTypes","unigramsBetweenEntities","bigrams","dependencyPathEdges","dependencyPathEdgesNearEntities"]

	finalChosenFeatures = []

	for stage in range(3):
		bestF1,bestFeature = -1,-1
		for feature in featureChoice:
			chosenFeatures = finalChosenFeatures + [feature]
			classifier = kindred.RelationClassifier(useBuilder=useBuilder,features=chosenFeatures)
			classifier.train(trainData)
		
			predictedRelations = classifier.predict(testData_TextAndEntities)
		
			evaluator = Evaluator()
			f1score = evaluator.evaluate(testData_Relations, predictedRelations, metric='f1score', display=False)
			print(stage,feature,f1score)

			if f1score > bestF1:
				bestF1 = f1score
				bestFeature = feature

		featureChoice.remove(bestFeature)
		finalChosenFeatures.append(bestFeature)

if __name__ == '__main__':
	print("BB3")
	_featureBuilding(True)
	print("SeeDev")
	_featureBuilding(False)

