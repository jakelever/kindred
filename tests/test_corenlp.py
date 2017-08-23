import pytest
from kindred.pycorenlp import StanfordCoreNLP
from kindred.Dependencies import initializeCoreNLP

def test_corenlpOutputError():
	initializeCoreNLP()
	nlp = StanfordCoreNLP('http://localhost:9000')
	#text = 'My friend will pay.'
	#text = 'Mein Freund wird bezahlen.'
	text = u"The quick brown fox jumped over the lazy dog"
	malformedannotators = 'tokenize,ssplit,pos,banana'

	with pytest.raises(RuntimeError) as excinfo:
		output = nlp.annotate(text,properties={'annotators': malformedannotators,'outputFormat': 'json','weird':'weird'})
	assert excinfo.value.args == ("CoreNLP Error. Last output (possibly truncated): Could not handle incoming annotation",)


