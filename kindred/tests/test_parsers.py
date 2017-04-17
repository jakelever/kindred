from nltk.parse.stanford import StanfordDependencyParser

def test_stanford_dependency_parser():
	dep_parser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

	print [ parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.") ]


#test_stanford_dependency_parser()
