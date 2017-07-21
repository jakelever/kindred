import os

import kindred
import kindred.Dependencies
from kindred.Parser import Parser

from kindred.datageneration import generateData,generateTestData

def assertEntityWithLocation(entityWithLocation,expectedType,expectedLocs,expectedSourceEntityID):
	assert isinstance(entityWithLocation, tuple)
	assert len(entityWithLocation) == 2
	entity,location = entityWithLocation

	assert isinstance(entity, kindred.Entity)
	assert isinstance(location, list)

	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert location == expectedLocs, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_simpleSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">lung</cancer> and unknown <cancer id="2">cancers</cancer>'
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == 1
	
	sentence = doc.sentences[0]
	assert isinstance(sentence,kindred.Sentence)
	
	expectedWords = "Erlotinib is a common treatment for lung and unknown cancers".split()
	assert isinstance(sentence.tokens,list)
	assert len(expectedWords) == len(sentence.tokens)
	for w,t in zip(expectedWords,sentence.tokens):
		assert isinstance(t,kindred.Token)
		assert len(t.lemma) > 0
		assert w == t.word
	
	assert isinstance(sentence.entitiesWithLocations,list)
	assert len(sentence.entitiesWithLocations) == 2
	assertEntityWithLocation(sentence.entitiesWithLocations[0],'drug',[0],'1')
	assertEntityWithLocation(sentence.entitiesWithLocations[1],'cancer',[6,9],'2')
	
	assert isinstance(sentence.dependencies,list)
	assert len(sentence.dependencies) > 0
	
	
def test_twoSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>.'
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == 2
	
	# Check types
	for sentence in doc.sentences:
		assert isinstance(sentence,kindred.Sentence)
		assert isinstance(sentence.tokens,list)
		for t in sentence.tokens:
			assert isinstance(t,kindred.Token)
			assert len(t.lemma) > 0
		assert isinstance(sentence.entitiesWithLocations,list)
		assert isinstance(sentence.dependencies,list)
		assert len(sentence.dependencies) > 0
		
		
	# First sentence
	expectedWords = "Erlotinib is a common treatment for NSCLC .".split()
	sentence0 = doc.sentences[0]
	assert len(expectedWords) == len(sentence0.tokens)
	for w,t in zip(expectedWords,sentence0.tokens):
		assert w == t.word
		
	assert isinstance(sentence0.entitiesWithLocations,list)
	assert len(sentence0.entitiesWithLocations) == 2
	assertEntityWithLocation(sentence0.entitiesWithLocations[0],'drug',[0],'1')
	assertEntityWithLocation(sentence0.entitiesWithLocations[1],'cancer',[6],'2')
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	sentence1 = doc.sentences[1]
	
	assert len(expectedWords) == len(sentence1.tokens)
	for w,t in zip(expectedWords,sentence1.tokens):
		assert w == t.word
		
	assert isinstance(sentence1.entitiesWithLocations,list)
	assert len(sentence1.entitiesWithLocations) == 2
	assertEntityWithLocation(sentence1.entitiesWithLocations[0],'drug',[0],'3')
	assertEntityWithLocation(sentence1.entitiesWithLocations[1],'disease',[6],'4')

def test_largeSentence():
	repeatCount = 500
	singleSentence = 'Erlotinib is a common treatment for lung and unknown cancers.'
	text = " ".join( [ singleSentence for _ in range(repeatCount) ] )
	corpus = kindred.Corpus(text)
	
	parser = Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == repeatCount

if __name__ == '__main__':
	test_largeSentence()
	
