from nltk.parse.stanford import StanfordDependencyParser
import kindred.Dependencies
import os

def test_stanford_dependency_parser():
	kindred.Dependencies.initializeStanfordParser()
	
	depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

	#print [ parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.") ]
	text = ["Colourless green ideas sleep furiously"]
	depParses = depParser.parse(text)
	depParses = list(depParses)
	assert len(depParses) == 1
	
	depParse = depParses[0]
	assert depParse.tree().__str__() == "(sleep (ideas Colourless green) furiously)"


if __name__ == '__main__':
	test_stanford_dependency_parser()
	