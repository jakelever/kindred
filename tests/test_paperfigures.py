import kindred

from kindred.datageneration import generateData,generateTestData

def _bionlpst_bb3_testSet():
	trainData = kindred.bionlpst.load('2016-BB3-event-train')
	devData = kindred.bionlpst.load('2016-BB3-event-dev')
	testData = kindred.bionlpst.load('2016-BB3-event-test')
	
	trainAndDevData = trainData + devData

	print("Starting training...")
	classifier = kindred.RelationClassifier(useBuilder=True)
	#classifier = RelationClassifier(useBuilder=False)
	classifier.train(trainAndDevData)

	print("Predicting training...")
	predictedRelations = classifier.predict(testData) #devData_TextAndEntities)
	
	print("Saving...")
	outDir = 'out.BB3'
	kindred.save(testData,'standoff',outDir,predictedRelations=predictedRelations)
	
	
def _bionlpst_seedev_testSet():	
	trainData = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devData = kindred.bionlpst.load('2016-SeeDev-binary-dev')
	testData = kindred.bionlpst.load('2016-SeeDev-binary-test')
	
	trainAndDevData = trainData + devData

	print("Starting training...")
	classifier = kindred.RelationClassifier()
	classifier.train(trainAndDevData)

	print("Predicting training...")
	predictedRelations = classifier.predict(testData) #devData_TextAndEntities)
	
	print("Saving...")
	outDir = 'out.SeeDev'
	kindred.save(testData,'standoff',outDir,predictedRelations=predictedRelations)
	
def _nary():	
	trainData = kindred.BioNLPSTData('2016-SeeDev-binary-training_and_development')
	testData = kindred.BioNLPSTData('2016-SeeDev-binary-test')
	
	classifier_merge = kindred.RelationClassifier(naryMethod='merge')
	classifier_merge.train(trainData)
	predictedRelations_merge = classifier_merge.predict(testData)
	kindred.saveST('BB3-predictions-merge/',testData,predictedRelations_merge)
	
	classifier_combined = kindred.RelationClassifier(naryMethod='combine')
	classifier_combined.train(trainData)
	predictedRelations_combined = classifier_combined.predict(testData)
	kindred.saveST('BB3-predictions-combined/',testData,predictedRelations_combined)
	
if __name__ == '__main__':
	_bionlpst_seedev_testSet()
	_bionlpst_bb3_testSet()

