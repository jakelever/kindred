import os
#from nltk.parse.stanford import StanfordDependencyParser

import kindred
import kindred.Dependencies
from kindred.Parser_corenlp import Parser

from kindred.datageneration import generateData,generateTestData

def assertProcessedEntity(entity,expectedType,expectedLocs,expectedSourceEntityID):
	assert isinstance(entity,kindred.ProcessedEntity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.entityLocs == expectedLocs, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def _stanfordDependencyParser():
	kindred.Dependencies.initializeStanfordParser()
		
	depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

	#print [ parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.") ]
	text = ["Colourless green ideas sleep furiously"]
	depParses = depParser.parse(text)
	depParses = list(depParses)
	assert len(depParses) == 1
	
	depParse = depParses[0]
	assert depParse.tree().__str__() == "(sleep (ideas Colourless green) furiously)"

def _maltParser():
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
	
	assert isinstance(processedSentence.processedEntities,list)
	assert len(processedSentence.processedEntities) == 2
	assertProcessedEntity(processedSentence.processedEntities[0],'drug',[0],1)
	assertProcessedEntity(processedSentence.processedEntities[1],'cancer',[6,9],2)
	
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
		
	assert isinstance(processedSentence0.processedEntities,list)
	assert len(processedSentence0.processedEntities) == 2
	assertProcessedEntity(processedSentence0.processedEntities[0],'drug',[0],1)
	assertProcessedEntity(processedSentence0.processedEntities[1],'cancer',[6],2)
	
	# Second sentence	
	expectedWords = "Aspirin is the main cause of boneitis .".split()
	processedSentence1 = processedSentences[1]
	
	assert len(expectedWords) == len(processedSentence1.tokens)
	for w,t in zip(expectedWords,processedSentence1.tokens):
		assert w == t.word
		
	assert isinstance(processedSentence1.processedEntities,list)
	assert len(processedSentence1.processedEntities) == 2
	assertProcessedEntity(processedSentence1.processedEntities[0],'drug',[0],3)
	assertProcessedEntity(processedSentence1.processedEntities[1],'disease',[6],4)

#TODO: Test parser with relations
#if test_sentenceParseWithRelations():
#	assert False

#@profile
def runPerfTest():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>lung</cancer> and unknown <cancer id=2>cancers</cancer>."
	text = " ".join([ text for _ in xrange(100)] )
	data = [ kindred.TextAndEntityData(text) for _ in range(2) ]
	
	parser = Parser()
	processedSentences = parser.parse(data)

if __name__ == '__main__':
	#test_stanfordDependencyParser()
	#test_maltParser()
	#text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>lung</cancer> and unknown <cancer id=2>cancers</cancer>"
	#data = [ kindred.TextAndEntityData(text) for _ in range(2) ]
	
	#parser = Parser()
	#processedSentences = parser.parse(data)
	runPerfTest()
	test_stanfordDependencyParser()
	