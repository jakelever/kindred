import kindred
import random
import kindred.utils
#from kindred import TextAndEntityData

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

def test_convertTaggedText():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug>Erlotinib</drug> is a common treatment for <cancer>NSCLC</cancer>"
	converted = kindred.TextAndEntityData(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=1,text='Erlotinib',start=0,end=9)
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=2,text='NSCLC',start=36,end=41)

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for NSCLC"

def test_convertedTaggedTextWithRelations():
	text = "<drug id=5>Erlotinib</drug> is a common treatment for <cancer id=6>NSCLC</cancer>"
	relations = [ ('treats',5,6) ]

	converted = kindred.RelationData(text,relations)
	assert isinstance(converted,kindred.RelationData)

	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=5,text='Erlotinib',start=0,end=9)
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=6,text='NSCLC',start=36,end=41)

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

	assert converted.getRelations() == relations

def test_unicodeCheck():
	assert False
	
def test_exportToST():
	assert False

def test_simpleRelationCheck():
	random.seed(1)

	positivePatterns = ["<drug id=1>DRUG</drug> treats <disease id=2>DISEASE</disease>",
						"<drug id=1>DRUG</drug> is a common treatment for <disease id=2>DISEASE</disease>",
						"<drug id=1>DRUG</drug> is often used for <disease id=2>DISEASE</disease>",
						"<disease id=2>DISEASE</disease> can be treated with <drug id=1>DRUG</drug>"]
	negativePatterns = ["<drug id=1>DRUG</drug> and <disease id=2>DISEASE</disease> were discovered by the same researcher",
						"<drug id=1>DRUG</drug> is the main cause of <disease id=2>DISEASE</disease>",
						"<drug id=1>DRUG</drug> failed clinical trials for <disease id=2>DISEASE</disease>",
						"<disease id=2>DISEASE</disease> is a known side effect of <drug id=1>DRUG</drug>"]
						
	fakeDrugNames = ['bmzvpvwbpw','pehhjnlvve''wbjccovflf','usckfljzxu','ruswdgzajr','vgypkemhjr','oxzbaapqct','elvptnpvyc']
	fakeDiseaseNames = ['gnorcyvmer','hfymprbifs','ootopaoxbg','knetvjnjun','kfjqxlpvew','zgwivlcmly','kneqlzjegs','kyekjnkrfo']
	
	positiveCount = 100
	negativeCount = 100
	totalCount = positiveCount + negativeCount
	
	data = []
	for _ in range(100):
		text = random.choice(positivePatterns)
		text = text.replace('DRUG',random.choice(fakeDrugNames))
		text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
		
		relations = [ (1,2,'treats') ]
		
		converted = kindred.utils.convertTaggedTextAndRelations(text,relations)
		data.append(converted)
		
	for _ in range(100):
		text = random.choice(negativePatterns)
		text = text.replace('DRUG',random.choice(fakeDrugNames))
		text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
		
		relations = [ ]
		
		converted = kindred.utils.convertTaggedTextAndRelations(text,relations)
		data.append(converted)
		
	trainIndices = random.sample(range(totalCount),totalCount/2)
	testIndices = [ i for i in range(totalCount) if not i in trainIndices ]
	
	trainData = [ data[i] for i in trainIndices ]
	testData = [ data[i] for i in testIndices ]
	
	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]
	
	model = kindred.Model()
	model.train(trainData)
	
	predictedRelations = model.predict(testData)
	f1score = kindred.evaluate(dev_data.getRelations(), predictionRelations, metric='f1score')
	assert f1score > 0.5
	
if __name__ == '__main__':
	test_convertedTaggedTextWithRelations()
