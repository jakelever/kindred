import kindred

import hashlib

# random module is not consistent across platforms
# Based on idea from:
# https://stackoverflow.com/questions/9023660/how-to-generate-a-repeatable-random-number-sequence
hashVal = b'seed'
def customSeed(seed):
	global hashVal
	assert isinstance(seed,bytes)
	hashVal = seed

def customRandom():
	global hashVal
	hashVal = hashlib.md5(hashVal).digest()
	
	if isinstance(hashVal,str):
		num = 256*ord(hashVal[0]) + ord(hashVal[1])
	else:
		num = 256*hashVal[0] + hashVal[1]
		
	return num/float(256*256)

def customChoice(seq):
	index = int(customRandom() * len(seq))
	return seq[index]

def customSample(population,k):
	listclone = list(population)
	assert k <= len(population)
	chosen = []
	for i in range(k):
		choice = int(customRandom() * len(listclone) )
		item = listclone.pop(choice)
		chosen.append(item)
	return chosen

def generateData(positiveCount=100,negativeCount=100,relTypes=1):
	customSeed(b'seed')
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
	
	relNames = [ "treats_%d" % i for i in range(relTypes) ]

	entityID = 1
	corpus = kindred.Corpus()
	for _ in range(positiveCount):
		text = customChoice(positivePatterns)
		text = text.replace('DRUG',customChoice(fakeDrugNames))
		text = text.replace('DISEASE',customChoice(fakeDiseaseNames))
		
		text = text.replace('ID1',str(entityID))
		text = text.replace('ID2',str(entityID+1))
		#relations = [ kindred.Relation('treats',[entityID,entityID+1]) ]

		relName = customChoice(relNames)
		text += '<relation type="%s" subj="%d" obj="%d" />' % (relName,entityID,entityID+1)
		
		entityID += 2
		
		converted = kindred.Document(text)
		corpus.addDocument(converted)
		
	halfNegativeCount = int(negativeCount/2.0)
	for _ in range(halfNegativeCount):
		combinedText = ""
		for _ in range(2):
			text = customChoice(negativePatterns)
			text = text.replace('DRUG',customChoice(fakeDrugNames))
			text = text.replace('DISEASE',customChoice(fakeDiseaseNames))
			
			text = text.replace('ID1',str(entityID))
			text = text.replace('ID2',str(entityID+1))
			entityID += 2
		
			combinedText = "%s %s" % (combinedText,text)
		
		converted = kindred.Document(combinedText)
		corpus.addDocument(converted)
		
	return corpus
	
def generateTestData(positiveCount = 100,negativeCount = 100, relTypes = 1):
	customSeed(b'seed')
	corpus = generateData(positiveCount, negativeCount, relTypes)
	docCount = len(corpus.documents)
	halfDataCount = int(docCount/2.0)
	trainIndices = customSample(range(docCount),halfDataCount)
	testIndices = [ i for i in range(docCount) if not i in trainIndices ]

	trainCorpus = kindred.Corpus()
	testCorpus = kindred.Corpus()
	for i in trainIndices:
		trainCorpus.addDocument(corpus.documents[i])
	for i in testIndices:
		testCorpus.addDocument(corpus.documents[i])

	return trainCorpus,testCorpus

