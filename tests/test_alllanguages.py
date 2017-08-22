# -*- coding: utf-8 -*-

import kindred
from kindred.pycorenlp import StanfordCoreNLP
import json
import os
import pytest

from kindred.Dependencies import initializeCoreNLP
import kindred.Dependencies

def getTestData(language):
	acceptedLanguages = ['arabic','chinese','english','french','german','spanish']
	assert language in acceptedLanguages

	if language == 'arabic':
		twoSentences = u"أنا أحب اللون الأزرق. كيف حالك؟"
		expected = {}
		expected['word'] = [[u'\u0627\u0646\u0627', u'\u0627\u062d\u0628', u'\u0627\u0644\u0644\u0648\u0646', u'\u0627\u0644\u0627\u0632\u0631\u0642', u'.'], [u'\u0643\u064a\u0641', u'\u062d\u0627\u0644', u'\u0643', u'?']]
		expected['lemma'] = [[u'\u0627\u0646\u0627', u'\u0627\u062d\u0628', u'\u0627\u0644\u0644\u0648\u0646', u'\u0627\u0644\u0627\u0632\u0631\u0642', u'.'], [u'\u0643\u064a\u0641', u'\u062d\u0627\u0644', u'\u0643', u'?']]
		expected['partofspeech'] = [[u'PRP', u'VBP', u'DTNN', u'DTJJ', u'PUNC'], [u'WRB', u'NN', u'PRP$', u'PUNC']]
		expected['startPos'] = [[0, 4, 8, 14, 20], [22, 26, 29, 30]]
		expected['endPos'] = [[3, 7, 13, 20, 21], [25, 29, 30, 31]]
		expected['dependencies'] = [[(-1, 1, u'ROOT'), (1, 0, u'nsubj'), (3, 2, u'compound'), (1, 3, u'dobj'), (1, 4, u'punct')], [(-1, 0, u'ROOT'), (2, 1, u'compound'), (0, 2, u'dep'), (2, 3, u'punct')]]

	elif language == 'chinese':
		twoSentences = u"我喜歡走路。他看電視。"
		expected = {}
		expected['word'] = [[u'\u6211\u559c\u6b61', u'\u8d70\u8def', u'\u3002'], [u'\u4ed6', u'\u770b', u'\u96fb\u8996', u'\u3002']]
		expected['lemma'] = [[u'\u6211\u559c\u6b61', u'\u8d70\u8def', u'\u3002'], [u'\u4ed6', u'\u770b', u'\u96fb\u8996', u'\u3002']]
		expected['partofspeech'] = [[u'NN', u'VV', u'PU'], [u'PN', u'VV', u'NN', u'PU']]
		expected['startPos'] = [[0, 3, 5], [6, 7, 8, 10]]
		expected['endPos'] = [[3, 5, 6], [7, 8, 10, 11]]
		expected['dependencies'] = [[(-1, 1, u'ROOT'), (1, 0, u'nsubj'), (1, 2, u'punct')], [(-1, 1, u'ROOT'), (1, 0, u'nsubj'), (1, 2, u'dobj'), (1, 3, u'punct')]]

	elif language == 'english':
		twoSentences = "Who controls the past controls the future. Who controls the present controls the past."
		expected = {}
		expected['word'] = [[u'Who', u'controls', u'the', u'past', u'controls', u'the', u'future', u'.'], [u'Who', u'controls', u'the', u'present', u'controls', u'the', u'past', u'.']]
		expected['lemma'] = [[u'who', u'control', u'the', u'past', u'control', u'the', u'future', u'.'], [u'who', u'control', u'the', u'present', u'control', u'the', u'past', u'.']]
		expected['partofspeech'] = [[u'WP', u'VBZ', u'DT', u'JJ', u'NNS', u'DT', u'NN', u'.'], [u'WP', u'VBZ', u'DT', u'JJ', u'NNS', u'DT', u'NN', u'.']]
		expected['startPos'] = [[0, 4, 13, 17, 22, 31, 35, 41], [43, 47, 56, 60, 68, 77, 81, 85]]
		expected['endPos'] = [[3, 12, 16, 21, 30, 34, 41, 42], [46, 55, 59, 67, 76, 80, 85, 86]]
		expected['dependencies'] = [[(-1, 1, u'ROOT'), (1, 0, u'nsubj'), (4, 2, u'det'), (4, 3, u'amod'), (1, 4, u'dobj'), (6, 5, u'det'), (4, 6, u'dep'), (1, 7, u'punct')], [(-1, 1, u'ROOT'), (1, 0, u'nsubj'), (4, 2, u'det'), (4, 3, u'amod'), (1, 4, u'dobj'), (6, 5, u'det'), (1, 6, u'nmod:tmod'), (1, 7, u'punct')]]

	elif language == 'french':
		twoSentences = u"À mauvais ouvrier point de bon outil. Donnant donnant."
		expected = {}
		expected['word'] = [[u'\xc0', u'mauvais', u'ouvrier', u'point', u'de', u'bon', u'outil', u'.'], [u'Donnant', u'donnant', u'.']]
		expected['lemma'] = [[u'\xe0', u'mauvais', u'ouvrier', u'point', u'de', u'bon', u'outil', u'.'], [u'donnant', u'donnant', u'.']]
		expected['partofspeech'] = [[u'P', u'ADJ', u'NC', u'N', u'P', u'ADJ', u'NC', u'PUNC'], [u'VPR', u'VPR', u'PUNC']]
		expected['startPos'] = [[0, 2, 10, 18, 24, 27, 31, 36], [38, 46, 53]]
		expected['endPos'] = [[1, 9, 17, 23, 26, 30, 36, 37], [45, 53, 54]]
		expected['dependencies'] = [[(-1, 3, u'ROOT'), (2, 0, u'case'), (2, 1, u'amod'), (3, 2, u'nmod'), (6, 4, u'case'), (6, 5, u'amod'), (3, 6, u'nmod'), (3, 7, u'punct')], [(-1, 0, u'ROOT'), (0, 1, u'xcomp'), (0, 2, u'punct')]]
	elif language == 'german':
		twoSentences = u"Aller Anfang ist schwer. Des Teufels liebstes Möbelstück ist die lange Bank."
		expected = {}
		expected['word'] = [[u'Aller', u'Anfang', u'ist', u'schwer', u'.'], [u'Des', u'Teufels', u'liebstes', u'M\xf6belst\xfcck', u'ist', u'die', u'lange', u'Bank', u'.']]
		expected['lemma'] = [[u'aller', u'anfang', u'ist', u'schwer', u'.'], [u'des', u'teufels', u'liebstes', u'm\xf6belst\xfcck', u'ist', u'die', u'lange', u'bank', u'.']]
		expected['partofspeech'] = [[u'PIDAT', u'NN', u'VAFIN', u'ADJD', u'$.'], [u'ART', u'NN', u'ADJA', u'NN', u'VAFIN', u'ART', u'ADJA', u'NN', u'$.']]
		expected['startPos'] = [[0, 6, 13, 17, 23], [25, 29, 37, 46, 57, 61, 65, 71, 75]]
		expected['endPos'] = [[5, 12, 16, 23, 24], [28, 36, 45, 56, 60, 64, 70, 75, 76]]
		expected['dependencies'] = [[(-1, 3, u'ROOT'), (1, 0, u'det'), (3, 1, u'nmod'), (3, 2, u'cop'), (3, 4, u'punct')], [(-1, 7, u'ROOT'), (3, 0, u'det'), (3, 1, u'amod'), (3, 2, u'amod'), (7, 3, u'nsubj'), (7, 4, u'cop'), (7, 5, u'det'), (7, 6, u'amod'), (7, 8, u'punct')]]

	elif language == 'spanish':
		twoSentences = u"A la ocasión la pintan calva. ¡Médico, cúrate a ti mismo!"
		expected = {}
		expected['word'] = [[u'A', u'la', u'ocasi\xf3n', u'la', u'pintan', u'calva', u'.'], [u'\xa1', u'M\xe9dico', u',', u'cura', u'te', u'a', u'ti', u'mismo', u'!']]
		expected['lemma'] = [[u'a', u'la', u'ocasi\xf3n', u'la', u'pintan', u'calva', u'.'], [u'\xa1', u'm\xe9dico', u',', u'cura', u'te', u'a', u'ti', u'mismo', u'!']]
		expected['partofspeech'] = [[u'sp000', u'da0000', u'nc0s000', u'da0000', u'nc0s000', u'nc0s000', u'fp'], [u'faa', u'np00000', u'fc', u'nc0s000', u'pp000000', u'sp000', u'pp000000', u'pi000000', u'fat']]
		expected['startPos'] = [[0, 2, 5, 13, 16, 23, 28], [30, 31, 37, 39, 43, 46, 48, 51, 56]]
		expected['endPos'] = [[1, 4, 12, 15, 22, 28, 29], [31, 37, 38, 43, 45, 47, 50, 56, 57]]
		expected['dependencies'] = [[(-1, 2, u'ROOT'), (2, 0, u'case'), (2, 1, u'det'), (4, 3, u'det'), (2, 4, u'nsubj'), (4, 5, u'amod'), (2, 6, u'punct')], [(-1, 1, u'ROOT'), (1, 0, u'punct'), (1, 2, u'punct'), (1, 3, u'appos'), (3, 4, u'iobj'), (6, 5, u'case'), (3, 6, u'nmod'), (6, 7, u'amod'), (1, 8, u'punct')]]

	return twoSentences,expected

def quickCheck():
	initializeCoreNLP('chinese')
	nlp = StanfordCoreNLP('http://localhost:9000')
	#text = 'My friend will pay.'
	#text = 'Mein Freund wird bezahlen.'
	text = u"我喜歡走路。他看電視。"
	annotators = 'tokenize,ssplit,pos'
	output = nlp.annotate(text,properties={'annotators': annotators,'outputFormat': 'json'})
	print(json.dumps(output,indent=2))

def deleteLanguageFiles(language):
	acceptedLanguages = ['arabic','chinese','french','german','spanish']
	assert language in acceptedLanguages

	kindredDir = kindred.Dependencies.downloadDirectory
	coreNLPDir = os.path.join(kindredDir,'stanford-corenlp-full-2017-06-09')
	modelFile = os.path.join(coreNLPDir,'stanford-%s-corenlp-2017-06-09-models.jar' % language)

	if os.path.isfile(modelFile):
		os.remove(modelFile)

def test_parseWithoutDownload_arabic():
	language = 'arabic'
	deleteLanguageFiles(language)

	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language),)

def test_parseWithoutDownload_chinese():
	language = 'chinese'
	deleteLanguageFiles(language)

	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language),)

def test_parseWithoutDownload_french():
	language = 'french'
	deleteLanguageFiles(language)

	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language),)

def test_parseWithoutDownload_german():
	language = 'german'
	deleteLanguageFiles(language)

	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language),)

def test_parseWithoutDownload_spanish():
	language = 'spanish'
	deleteLanguageFiles(language)

	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language),)

def test_downloadArabic():
	kindred.downloadCoreNLPLanguage('arabic')

def test_downloadChinese():
	kindred.downloadCoreNLPLanguage('chinese')

def test_downloadFrench():
	kindred.downloadCoreNLPLanguage('french')

def test_downloadGerman():
	kindred.downloadCoreNLPLanguage('german')

def test_downloadSpanish():
	kindred.downloadCoreNLPLanguage('spanish')

def test_languageMismatch():
	runningLanguage,desiredLanguage = 'german','spanish'

	kindred.downloadCoreNLPLanguage(runningLanguage)
	kindred.Dependencies.initializeCoreNLP(runningLanguage)
	with pytest.raises(RuntimeError) as excinfo:
		runLanguageTest(language=desiredLanguage,killCoreNLPIfNeeded=False,doDownloadIfNeeded=True)
	expectedMessage = "CoreNLP currently running does not match the language (%s) requested by the parser. Please stop this CoreNLP instance and either launch the appropriate one or let Kindred launch one." % desiredLanguage
	assert excinfo.value.args == (expectedMessage,)
	
	kindred.Dependencies.killCoreNLP()

def runLanguageTest(language,killCoreNLPIfNeeded,doDownloadIfNeeded):
	twoSentences,expected = getTestData(language)

	if killCoreNLPIfNeeded and kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()

	if doDownloadIfNeeded:
		kindred.downloadCoreNLPLanguage(language)

	parser = kindred.Parser(language=language)
	corpus = kindred.Corpus(twoSentences)
	parser.parse(corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert len(doc.sentences) == 2

	letPass = False

	word = [ [ t.word for t in sentence.tokens ] for sentence in doc.sentences ]
	assert letPass or word == expected['word']

	lemma = [ [ t.lemma for t in sentence.tokens ] for sentence in doc.sentences ]
	assert letPass or lemma == expected['lemma']
	
	partofspeech = [ [ t.partofspeech for t in sentence.tokens ] for sentence in doc.sentences ]
	assert letPass or partofspeech == expected['partofspeech']

	startPos = [ [ t.startPos for t in sentence.tokens ] for sentence in doc.sentences ]
	assert letPass or startPos == expected['startPos']

	endPos = [ [ t.endPos for t in sentence.tokens ] for sentence in doc.sentences ]
	assert letPass or endPos == expected['endPos']

	dependencies = [ sentence.dependencies for sentence in doc.sentences ]
	assert letPass or dependencies == expected['dependencies']

	kindred.Dependencies.killCoreNLP()




def test_arabic():
	language = 'arabic'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_chinese():
	language = 'chinese'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_english():
	language = 'english'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)

def test_french():
	language = 'french'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_german():
	language = 'german'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)
	
def test_spanish():
	language = 'spanish'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)
	


if __name__ == '__main__':
	#quickCheck()
	test_chinese()

