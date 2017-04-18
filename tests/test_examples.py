import kindred
import random
#from kindred import TextAndEntityData
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Parser import Parser

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

def test_pubmed():
	assert False
	
def test_convertTaggedText():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug>Erlotinib</drug> is a common treatment for <cancer>NSCLC</cancer>"
	converted = kindred.TextAndEntityData(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=1,text='Erlotinib',pos=[(0,9)])
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=2,text='NSCLC',pos=[(36,41)])

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for NSCLC"
	
	
def test_convertTaggedTextWithSplitEntities():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>lung</cancer> and unknown <cancer id=2>cancers</cancer>"
	converted = kindred.TextAndEntityData(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=1,text='Erlotinib',pos=[(0,9)])
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=2,text='lung cancers',pos=[(36,40), (53,60)])

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for lung and unknown cancers"

def test_convertedTaggedTextWithRelations():
	text = "<drug id=5>Erlotinib</drug> is a common treatment for <cancer id=6>NSCLC</cancer>"
	relations = [ ('treats',5,6) ]

	converted = kindred.RelationData(text,relations)
	assert isinstance(converted,kindred.RelationData)

	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=5,text='Erlotinib',pos=[(0,9)])
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=6,text='NSCLC',pos=[(36,41)])

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

	assert converted.getRelations() == relations

def test_unicodeCheck():
	assert False
	
def test_exportToST():
	assert False

def generateData(positiveCount=100,negativeCount=100):
	random.seed(1)

	positivePatterns = ["<drug id=1>DRUG</drug> treats <disease id=2>DISEASE</disease>.",
						"<drug id=1>DRUG</drug> is a common treatment for <disease id=2>DISEASE</disease>.",
						"<drug id=1>DRUG</drug> is often used for <disease id=2>DISEASE</disease>.",
						"<disease id=2>DISEASE</disease> can be treated with <drug id=1>DRUG</drug>."]
	negativePatterns = ["<drug id=1>DRUG</drug> and <disease id=2>DISEASE</disease> were discovered by the same researcher.",
						"<drug id=1>DRUG</drug> is the main cause of <disease id=2>DISEASE</disease>.",
						"<drug id=1>DRUG</drug> failed clinical trials for <disease id=2>DISEASE</disease>.",
						"<disease id=2>DISEASE</disease> is a known side effect of <drug id=1>DRUG</drug>."]
						
	fakeDrugNames = ['bmzvpvwbpw','pehhjnlvve''wbjccovflf','usckfljzxu','ruswdgzajr','vgypkemhjr','oxzbaapqct','elvptnpvyc']
	fakeDiseaseNames = ['gnorcyvmer','hfymprbifs','ootopaoxbg','knetvjnjun','kfjqxlpvew','zgwivlcmly','kneqlzjegs','kyekjnkrfo']
	
	totalCount = positiveCount + negativeCount
	
	data = []
	for _ in range(positiveCount):
		text = random.choice(positivePatterns)
		text = text.replace('DRUG',random.choice(fakeDrugNames))
		text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
		
		relations = [ ('treats',1,2) ]
		
		converted = kindred.RelationData(text,relations)
		data.append(converted)
		
	for _ in range(negativeCount/2):
		combinedText = ""
		for _ in range(2):
			text = random.choice(negativePatterns)
			text = text.replace('DRUG',random.choice(fakeDrugNames))
			text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
			combinedText = "%s %s" % (combinedText,text)
		
		relations = [ ]
		
		converted = kindred.RelationData(combinedText,relations)
		data.append(converted)
		
	return data
	
def generateTestData(positiveCount = 100,negativeCount = 100):
	data = generateData(positiveCount, negativeCount)
		
	trainIndices = random.sample(range(len(data)),len(data)/2)
	testIndices = [ i for i in range(len(data)) if not i in trainIndices ]
	
	trainData = [ data[i] for i in trainIndices ]
	testData = [ data[i] for i in testIndices ]
	
	return trainData, testData
	
	
def test_simpleSentenceParse():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>lung</cancer> and unknown <cancer id=2>cancers</cancer>"
	data = [kindred.TextAndEntityData(text)]
	
	parser = Parser()
	processedSentences = parser.parse(data)
	
	assert isinstance(processedSentences,list)
	assert len(processedSentences) == 1
	
	processedSentence = processedSentences[0]
	assert isinstance(processedSentence,kindred.ProcessedSentence)
	
	expectedWords = "Erlotinib is a common treatment for lung and unknown cancers".split()
	assert isinstance(processedSentence.tokens,list)
	assert len(expectedWords) == len(processedSentence.tokens)
	for w,t in zip(expectedWords,processedSentence.tokens):
		assert isinstance(t,kindred.Token)
		assert len(t.lemma) > 0
		assert w == t.word
		
	assert isinstance(processedSentence.entityLocs,dict)
	assert isinstance(processedSentence.entityTypes,dict)
	
	assert processedSentence.entityLocs == {1: [0], 2: [6, 9]}
	assert processedSentence.entityTypes == {1: 'drug', 2: 'cancer'}
	
	assert isinstance(processedSentence.dependencies,list)
	assert len(processedSentence.dependencies) > 0
	
	
def test_twoSentenceParse():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>NSCLC</cancer>. <drug id=3>Aspirin</drug> is the main cause of <disease id=4>boneitis</disease>."
	data = [kindred.TextAndEntityData(text)]
	
	parser = Parser()
	processedSentences = parser.parse(data)
	
	assert isinstance(processedSentences,list)
	assert len(processedSentences) == 2
	
	# Check types
	for processedSentence in processedSentences:
		assert isinstance(processedSentence,kindred.ProcessedSentence)
		assert isinstance(processedSentence.tokens,list)
		for t in processedSentence.tokens:
			assert isinstance(t,kindred.Token)
			assert len(t.lemma) > 0
		assert isinstance(processedSentence.entityLocs,dict)
		assert isinstance(processedSentence.entityTypes,dict)
		assert isinstance(processedSentence.dependencies,list)
		assert len(processedSentence.dependencies) > 0
		
		
	# First sentence
	expectedWords = "Erlotinib is a common treatment for NSCLC .".split()
	processedSentence0 = processedSentences[0]
	assert len(expectedWords) == len(processedSentence0.tokens)
	for w,t in zip(expectedWords,processedSentence0.tokens):
		assert w == t.word
		
	assert processedSentence0.entityLocs == {1: [0], 2: [6]}
	assert processedSentence0.entityTypes == {1: 'drug', 2: 'cancer'}
	
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	processedSentence1 = processedSentences[1]
	
	assert len(expectedWords) == len(processedSentence1.tokens)
	for w,t in zip(expectedWords,processedSentence1.tokens):
		assert w == t.word
		
	assert processedSentence1.entityLocs == {3: [0], 4: [6]}
	assert processedSentence1.entityTypes == {3: 'drug', 4: 'disease'}
	
def test_simpleRelationCandidates():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>NSCLC</cancer>. <drug id=3>Aspirin</drug> is the main cause of <disease id=4>boneitis</disease> ."
	relations = [ ('treats',1,2) ]

	data = [kindred.RelationData(text,relations)]	
	
	candidateGenerator = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateGenerator.build(data)
	
	assert relTypes == [('treats', 2)]
	assert candidateClasses == [[1], 0, 0, 0]
	assert len(candidateRelations) == 4
	
	assert str(candidateRelations[0].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[1].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[2].processedSentence) == 'Aspirin is the main cause of boneitis .'
	assert str(candidateRelations[3].processedSentence) == 'Aspirin is the main cause of boneitis .'
	
	assert candidateRelations[0].entitiesInRelation == (1, 2)
	assert candidateRelations[1].entitiesInRelation == (2, 1)
	assert candidateRelations[2].entitiesInRelation == (3, 4)
	assert candidateRelations[3].entitiesInRelation == (4, 3)
	
def test_naryRelations():
	assert False
	
def test_simpleRelationCheck():
	trainData, testData = generateTestData()
	
	testData_TextAndEntities = [ d.getTextAndEntities() for d in testData ]
	testData_Relations = [ d.getRelations() for d in testData ]
	
	model = kindred.Model()
	model.train(trainData)
	
	predictedRelations = model.predict(testData)
	f1score = kindred.evaluate(dev_data.getRelations(), predictionRelations, metric='f1score')
	assert f1score > 0.5
	
	
if __name__ == '__main__':
	test_simpleRelationCandidates()
