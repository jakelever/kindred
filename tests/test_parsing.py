import os

import kindred
import kindred.Dependencies
from kindred.Parser import Parser

from kindred.datageneration import generateData,generateTestData

def assertProcessedEntity(entity,expectedType,expectedLocs,expectedSourceEntityID):
	assert isinstance(entity,kindred.ProcessedEntity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.entityLocs == expectedLocs, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_simpleSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">lung</cancer> and unknown <cancer id="2">cancers</cancer>'
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.processedSentences,list)
	assert len(doc.processedSentences) == 1
	
	processedSentence = doc.processedSentences[0]
	assert isinstance(processedSentence,kindred.ProcessedSentence)
	
	expectedWords = "Erlotinib is a common treatment for lung and unknown cancers".split()
	assert isinstance(processedSentence.tokens,list)
	assert len(expectedWords) == len(processedSentence.tokens)
	for w,t in zip(expectedWords,processedSentence.tokens):
		assert isinstance(t,kindred.Token)
		assert len(t.lemma) > 0
		assert w == t.word
	
	assert isinstance(processedSentence.processedEntities,list)
	assert len(processedSentence.processedEntities) == 2
	assertProcessedEntity(processedSentence.processedEntities[0],'drug',[0],'1')
	assertProcessedEntity(processedSentence.processedEntities[1],'cancer',[6,9],'2')
	
	assert isinstance(processedSentence.dependencies,list)
	assert len(processedSentence.dependencies) > 0
	
	
def test_twoSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>.'
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.processedSentences,list)
	assert len(doc.processedSentences) == 2
	
	# Check types
	for processedSentence in doc.processedSentences:
		assert isinstance(processedSentence,kindred.ProcessedSentence)
		assert isinstance(processedSentence.tokens,list)
		for t in processedSentence.tokens:
			assert isinstance(t,kindred.Token)
			assert len(t.lemma) > 0
		assert isinstance(processedSentence.processedEntities,list)
		assert isinstance(processedSentence.dependencies,list)
		assert len(processedSentence.dependencies) > 0
		
		
	# First sentence
	expectedWords = "Erlotinib is a common treatment for NSCLC .".split()
	processedSentence0 = doc.processedSentences[0]
	assert len(expectedWords) == len(processedSentence0.tokens)
	for w,t in zip(expectedWords,processedSentence0.tokens):
		assert w == t.word
		
	assert isinstance(processedSentence0.processedEntities,list)
	assert len(processedSentence0.processedEntities) == 2
	assertProcessedEntity(processedSentence0.processedEntities[0],'drug',[0],'1')
	assertProcessedEntity(processedSentence0.processedEntities[1],'cancer',[6],'2')
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	processedSentence1 = doc.processedSentences[1]
	
	assert len(expectedWords) == len(processedSentence1.tokens)
	for w,t in zip(expectedWords,processedSentence1.tokens):
		assert w == t.word
		
	assert isinstance(processedSentence1.processedEntities,list)
	assert len(processedSentence1.processedEntities) == 2
	assertProcessedEntity(processedSentence1.processedEntities[0],'drug',[0],'3')
	assertProcessedEntity(processedSentence1.processedEntities[1],'disease',[6],'4')

def test_largeSentence():
	repeatCount = 500
	singleSentence = 'Erlotinib is a common treatment for lung and unknown cancers.'
	text = " ".join( [ singleSentence for _ in range(repeatCount) ] )
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.processedSentences,list)
	assert len(doc.processedSentences) == repeatCount

if __name__ == '__main__':
	test_largeSentence()
	
