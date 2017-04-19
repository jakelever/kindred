import os
from nltk.parse.stanford import StanfordDependencyParser

import kindred
import kindred.Dependencies
from kindred.Parser import Parser

from kindred.datageneration import generateData,generateTestData

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.pos == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_stanfordDependencyParser():
	kindred.Dependencies.initializeStanfordParser()
		
	depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

	#print [ parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.") ]
	text = ["Colourless green ideas sleep furiously"]
	depParses = depParser.parse(text)
	depParses = list(depParses)
	assert len(depParses) == 1
	
	depParse = depParses[0]
	assert depParse.tree().__str__() == "(sleep (ideas Colourless green) furiously)"

def test_maltParser():
	kindred.Dependencies.initializeMaltParser()
	maltParser = kindred.Dependencies.getMaltParser()
	
	text = "Colourless green ideas sleep furiously"
	
	depParses = maltParser.parse(text.split())
	depParses = list(depParses)
	assert len(depParses) == 1
	
	depParse = depParses[0]
	assert depParse.tree().__str__() == "(sleep Colourless green ideas furiously)"


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
	
	assert processedSentence.processedEntities == [ kindred.ProcessedEntity('drug',[0],1,1) , kindred.ProcessedEntity('cancer',[6,9],2,2) ]
	
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
		assert isinstance(processedSentence.processedEntities,list)
		assert isinstance(processedSentence.dependencies,list)
		assert len(processedSentence.dependencies) > 0
		
		
	# First sentence
	expectedWords = "Erlotinib is a common treatment for NSCLC .".split()
	processedSentence0 = processedSentences[0]
	assert len(expectedWords) == len(processedSentence0.tokens)
	for w,t in zip(expectedWords,processedSentence0.tokens):
		assert w == t.word
		
	assert processedSentence0.processedEntities == [ kindred.ProcessedEntity('drug',[0],1,1) , kindred.ProcessedEntity('cancer',[6],2,2) ]
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	processedSentence1 = processedSentences[1]
	
	assert len(expectedWords) == len(processedSentence1.tokens)
	for w,t in zip(expectedWords,processedSentence1.tokens):
		assert w == t.word
		
	assert processedSentence1.processedEntities == [ kindred.ProcessedEntity('drug',[0],3,3) , kindred.ProcessedEntity('disease',[6],4,4) ]

#TODO: Test parser with relations
#if test_sentenceParseWithRelations():
#	assert False

if __name__ == '__main__':
	#test_stanfordDependencyParser()
	test_maltParser()
	
