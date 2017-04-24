import random

import kindred

def generateData(positiveCount=100,negativeCount=100):
	random.seed(1)

	positivePatterns = ['<drug id="ID1">DRUG</drug> treats <disease id="ID2">DISEASE</disease>.',
						'<drug id="ID1">DRUG</drug> is a common treatment for <disease id="ID2">DISEASE</disease>.',
						'<drug id="ID1">DRUG</drug> is often used for <disease id="ID2">DISEASE</disease>.',
						'<disease id="ID2">DISEASE</disease> can be treated with <drug id="ID1">DRUG</drug>.']
	negativePatterns = ['<drug id="ID1">DRUG</drug> and <disease2 id="ID2">DISEASE</disease2> were discovered by the same researcher.',
						'<drug id="ID1">DRUG</drug> is the main cause of <disease2 id="ID2">DISEASE</disease2>.',
						'<drug id="ID1">DRUG</drug> failed clinical trials for <disease2 id="ID2">DISEASE</disease2>.',
						'<disease2 id="ID2">DISEASE</disease2> is a known side effect of <drug id="ID1">DRUG</drug>.']
						
	fakeDrugNames = ['bmzvpvwbpw','pehhjnlvve''wbjccovflf','usckfljzxu','ruswdgzajr','vgypkemhjr','oxzbaapqct','elvptnpvyc']
	fakeDiseaseNames = ['gnorcyvmer','hfymprbifs','ootopaoxbg','knetvjnjun','kfjqxlpvew','zgwivlcmly','kneqlzjegs','kyekjnkrfo']
	
	totalCount = positiveCount + negativeCount
	
	entityID = 1
	data = []
	for _ in range(positiveCount):
		text = random.choice(positivePatterns)
		text = text.replace('DRUG',random.choice(fakeDrugNames))
		text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
		
		text = text.replace('ID1',str(entityID))
		text = text.replace('ID2',str(entityID+1))
		#relations = [ kindred.Relation('treats',[entityID,entityID+1]) ]

		text += '<relation type="%s" subj="%d" obj="%d" />' % ('treats',entityID,entityID+1)
		
		entityID += 2
		
		converted = kindred.RelationData(text)
		data.append(converted)
		
	halfNegativeCount = int(negativeCount/2.0)
	for _ in range(halfNegativeCount):
		combinedText = ""
		for _ in range(2):
			text = random.choice(negativePatterns)
			text = text.replace('DRUG',random.choice(fakeDrugNames))
			text = text.replace('DISEASE',random.choice(fakeDiseaseNames))
			
			text = text.replace('ID1',str(entityID))
			text = text.replace('ID2',str(entityID+1))
			entityID += 2
		
			combinedText = "%s %s" % (combinedText,text)
		
		converted = kindred.RelationData(combinedText)
		data.append(converted)
		
	return data
	
def generateTestData(positiveCount = 100,negativeCount = 100):
	data = generateData(positiveCount, negativeCount)
		
	halfDataCount = int(len(data)/2.0)
	trainIndices = random.sample(range(len(data)),halfDataCount)
	testIndices = [ i for i in range(len(data)) if not i in trainIndices ]
	
	trainData = [ data[i] for i in trainIndices ]
	testData = [ data[i] for i in testIndices ]
	
	return trainData, testData
