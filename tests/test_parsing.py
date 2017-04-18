from nltk.parse.stanford import StanfordDependencyParser
import kindred.Dependencies
import os
from nltk import internals

def test_stanfordDependencyParser():
	kindred.Dependencies.initializeStanfordParser()
	
	for var in ['JAVAHOME', 'JAVA_HOME']:
		if var in os.environ:
			print("os.environ[%s] = %s" % (var,os.environ[var]))
		else:
			print("os.environ[%s] not set" % (var))
			
	print("internals._java_bin", internals._java_bin)
	internals.config_java()
	print("internals._java_bin", internals._java_bin)
	
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

if __name__ == '__main__':
	#test_stanfordDependencyParser()
	test_maltParser()
	