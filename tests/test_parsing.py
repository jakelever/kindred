# -*- coding: utf-8 -*- 
import os

import kindred
from kindred.datageneration import generateData,generateTestData

def assertEntityWithLocation(entityAnnotation,expectedType,expectedLocs,expectedSourceEntityID):
	assert isinstance(entityAnnotation,tuple)
	assert len(entityAnnotation) == 2
	
	entity,tokenIndices = entityAnnotation
	assert isinstance(entity, kindred.Entity)

	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
	assert tokenIndices == expectedLocs, "(%s) not as expected" % (entity.__str__())

def test_simpleSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">lung</cancer> and unknown <cancer id="2">cancers</cancer>'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	parser = kindred.Parser()
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
	
	assert isinstance(sentence.entityAnnotations,list)
	assert len(sentence.entityAnnotations) == 2
	assertEntityWithLocation(sentence.entityAnnotations[0],'drug',[0],'1')
	assertEntityWithLocation(sentence.entityAnnotations[1],'cancer',[6,9],'2')
	#assert(sentence.entityAnnotations) == False
	
	assert isinstance(sentence.dependencies,list)
	assert len(sentence.dependencies) > 0
	
def test_parsing_dependencyGraph():
	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	parser = kindred.Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == 1
	
	sentence = doc.sentences[0]
	assert isinstance(sentence,kindred.Sentence)
	
	expectedWords = "You need to turn in your homework by next week".split()
	assert isinstance(sentence.tokens,list)
	assert len(expectedWords) == len(sentence.tokens)
	for w,t in zip(expectedWords,sentence.tokens):
		assert isinstance(t,kindred.Token)
		assert len(t.lemma) > 0
		assert w == t.word
	
	assert isinstance(sentence.entityAnnotations,list)
	assert len(sentence.entityAnnotations) == 0
	
	assert isinstance(sentence.dependencies,list)
	expectedDependencies = [(1, 0, u'nsubj'), (1, 1, u'ROOT'), (3, 2, u'aux'), (1, 3, u'xcomp'), (3, 4, u'prt'), (6, 5, u'poss'), (3, 6, u'dobj'), (3, 7, u'prep'), (9, 8, u'amod'), (7, 9, u'pobj')]
	assert sentence.dependencies == expectedDependencies
	
def test_twoSentenceParse():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>.'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	parser = kindred.Parser()
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
		assert isinstance(sentence.entityAnnotations,list)
		assert isinstance(sentence.dependencies,list)
		assert len(sentence.dependencies) > 0
		
		
	# First sentence
	expectedWords = "Erlotinib is a common treatment for NSCLC .".split()
	sentence0 = doc.sentences[0]
	assert len(expectedWords) == len(sentence0.tokens)
	for w,t in zip(expectedWords,sentence0.tokens):
		assert w == t.word
		
	assert isinstance(sentence0.entityAnnotations,list)
	assert len(sentence0.entityAnnotations) == 2
	assertEntityWithLocation(sentence0.entityAnnotations[0],'drug',[0],'1')
	assertEntityWithLocation(sentence0.entityAnnotations[1],'cancer',[6],'2')
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	sentence1 = doc.sentences[1]
	
	assert len(expectedWords) == len(sentence1.tokens)
	for w,t in zip(expectedWords,sentence1.tokens):
		assert w == t.word
		
	assert isinstance(sentence1.entityAnnotations,list)
	assert len(sentence1.entityAnnotations) == 2
	assertEntityWithLocation(sentence1.entityAnnotations[0],'drug',[0],'3')
	assertEntityWithLocation(sentence1.entityAnnotations[1],'disease',[6],'4')

def test_largeSentence():
	repeatCount = 500
	singleSentence = 'Erlotinib is a common treatment for lung and unknown cancers.'
	text = " ".join( [ singleSentence for _ in range(repeatCount) ] )
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	parser = kindred.Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == repeatCount

def test_unicodeParse():
	text = u"<drug id='1'>Erlotinib</drug> is a common treatment for NF-κB positive <cancer id='2'>lung</cancer> and unknown <cancer id='2'>cancers</cancer>"
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	parser = kindred.Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == 1
	
	sentence = doc.sentences[0]
	assert isinstance(sentence,kindred.Sentence)
	
	expectedWords = u"Erlotinib is a common treatment for NF - κB positive lung and unknown cancers".split()
	assert isinstance(sentence.tokens,list)
	assert len(expectedWords) == len(sentence.tokens)
	for w,t in zip(expectedWords,sentence.tokens):
		assert isinstance(t,kindred.Token)
		assert len(t.lemma) > 0
		assert w == t.word
	
	assert isinstance(sentence.entityAnnotations,list)
	assert len(sentence.entityAnnotations) == 2
	assertEntityWithLocation(sentence.entityAnnotations[0],'drug',[0],'1')
	assertEntityWithLocation(sentence.entityAnnotations[1],'cancer',[10,13],'2')
	
	assert isinstance(sentence.dependencies,list)
	assert len(sentence.dependencies) > 0

def test_notunicode():
	singleSentence = 'Erlotinib is a common treatment for lung and unknown cancers.'
	corpus = kindred.Corpus(singleSentence)
	
	parser = kindred.Parser()
	parser.parse(corpus)
	
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert isinstance(doc.sentences,list)
	assert len(doc.sentences) == 1

if __name__ == '__main__':
	#test_largeSentence()
	test_parsing_dependencyGraph()
	
