# -*- coding: utf-8 -*-

import kindred
import json
import os
import pytest

def getTestData(language):
	acceptedLanguages = ['en','de','es','pt','fr','it','nl']
	assert language in acceptedLanguages, "Language for parser (%s) not in accepted languages: %s" % (language,str(acceptedLanguages))

	if language == 'en':
		twoSentences = "Who controls the past controls the future. Who controls the present controls the past."
		expected = {}
		expected['word'] = [[u'Who', u'controls', u'the', u'past', u'controls', u'the', u'future', u'.'], [u'Who', u'controls', u'the', u'present', u'controls', u'the', u'past', u'.']]
		expected['lemma'] = [[u'who', u'control', u'the', u'past', u'control', u'the', u'future', u'.'], [u'who', u'control', u'the', u'present', u'control', u'the', u'past', u'.']]
		expected['partofspeech'] = [[u'NOUN', u'VERB', u'DET', u'NOUN', u'VERB', u'DET', u'NOUN', u'PUNCT'], [u'NOUN', u'VERB', u'DET', u'ADJ', u'VERB', u'DET', u'NOUN', u'PUNCT']]
		expected['startPos'] = [[0, 4, 13, 17, 22, 31, 35, 41], [43, 47, 56, 60, 68, 77, 81, 85]]
		expected['endPos'] = [[3, 12, 16, 21, 30, 34, 41, 42], [46, 55, 59, 67, 76, 80, 85, 86]]
		expected['dependencies'] = [[(1, 0, u'nsubj'), (4, 1, u'csubj'), (3, 2, u'det'), (1, 3, u'dobj'), (4, 4, u'ROOT'), (6, 5, u'det'), (4, 6, u'dobj'), (4, 7, u'punct')], [(1, 0, u'nsubj'), (1, 1, u'ROOT'), (3, 2, u'det'), (4, 3, u'amod'), (1, 4, u'dobj'), (6, 5, u'det'), (4, 6, u'dobj'), (1, 7, u'punct')]]

	elif language == 'fr':
		twoSentences = u"À mauvais ouvrier point de bon outil. Donnant donnant."
		expected = {}
		expected['word'] = [[u'\xc0', u'mauvais', u'ouvrier', u'point', u'de', u'bon', u'outil', u'.'], [u'Donnant', u'donnant', u'.']]
		expected['lemma'] = [[u'\xe0', u'mauvais', u'ouvrier', u'poindre', u'de', u'bon', u'outil', u'.'], [u'donnant', u'donner', u'.']]
		expected['partofspeech'] = [[u'ADP', u'NOUN', u'ADJ', u'NOUN', u'ADP', u'ADJ', u'NOUN', u'PUNCT'], [u'VERB', u'VERB', u'PUNCT']]
		expected['startPos'] = [[0, 2, 10, 18, 24, 27, 31, 36], [38, 46, 53]]
		expected['endPos'] = [[1, 9, 17, 23, 26, 30, 36, 37], [45, 53, 54]]
		expected['dependencies'] = [[(1, 0, u'case'), (1, 1, u'ROOT'), (1, 2, u'amod'), (1, 3, u'amod'), (6, 4, u'case'), (6, 5, u'amod'), (1, 6, u'nmod'), (1, 7, u'punct')], [(0, 0, u'ROOT'), (0, 1, u'acl'), (0, 2, u'punct')]]

	elif language == 'de':
		twoSentences = u"Aller Anfang ist schwer. Des Teufels liebstes Möbelstück ist die lange Bank."
		expected = {}
		expected['word'] = [[u'Aller', u'Anfang', u'ist', u'schwer', u'.'], [u'Des', u'Teufels', u'liebstes', u'M\xf6belst\xfcck', u'ist', u'die', u'lange', u'Bank', u'.']]
		expected['lemma'] = [[u'aller', u'anfang', u'sein', u'schwer', u'.'], [u'des', u'Teufel', u'lieb', u'm\xf6belst\xfcck', u'sein', u'der', u'lang', u'bank', u'.']]
		expected['partofspeech'] = [[u'DET', u'NOUN', u'AUX', u'ADJ', u'PUNCT'], [u'DET', u'NOUN', u'ADJ', u'NOUN', u'AUX', u'DET', u'ADJ', u'NOUN', u'PUNCT']]
		expected['startPos'] = [[0, 6, 13, 17, 23], [25, 29, 37, 46, 57, 61, 65, 71, 75]]
		expected['endPos'] = [[5, 12, 16, 23, 24], [28, 36, 45, 56, 60, 64, 70, 75, 76]]
		expected['dependencies'] = [[(1, 0, u'nk'), (2, 1, u'sb'), (2, 2, u'ROOT'), (2, 3, u'pd'), (2, 4, u'punct')], [(1, 0, u'nk'), (3, 1, u'ag'), (3, 2, u'nk'), (4, 3, u'pd'), (4, 4, u'ROOT'), (7, 5, u'nk'), (7, 6, u'nk'), (4, 7, u'pd'), (4, 8, u'punct')]]

	elif language == 'es':
		twoSentences = u"A la ocasión la pintan calva. ¡Médico, cúrate a ti mismo!"
		expected = {}
		expected['word'] = [[u'A', u'la', u'ocasi\xf3n', u'la', u'pintan', u'calva', u'.'], [u'\xa1', u'M\xe9dico', u',', u'c\xfarate', u'a', u'ti', u'mismo', u'!']]
		expected['lemma'] = [[u'a', u'lo', u'ocasi\xf3n', u'lo', u'pintar', u'calvo', u'.'], [u'\xa1', u'm\xe9dico', u',', u'c\xfarate', u'a', u'ti', u'mismo', u'!']]
		expected['partofspeech'] = [[u'ADP', u'DET', u'NOUN', u'DET', u'VERB', u'NOUN', u'PUNCT'], [u'PUNCT', u'PROPN', u'PUNCT', u'VERB', u'ADP', u'PRON', u'PRON', u'PUNCT']]
		expected['startPos'] = [[0, 2, 5, 13, 16, 23, 28], [30, 31, 37, 39, 46, 48, 51, 56]]
		expected['endPos'] = [[1, 4, 12, 15, 22, 28, 29], [31, 37, 38, 45, 47, 50, 56, 57]]
		expected['dependencies'] = [[(2, 0, u'case'), (2, 1, u'det'), (4, 2, u'iobj'), (4, 3, u'obj'), (4, 4, u'ROOT'), (4, 5, u'nsubj'), (4, 6, u'punct')], [(1, 0, u'punct'), (1, 1, u'ROOT'), (3, 2, u'punct'), (1, 3, u'appos'), (5, 4, u'case'), (3, 5, u'obj'), (5, 6, u'amod'), (1, 7, u'punct')]]

	elif language == 'it':
		twoSentences = u"Ogni cosa si compra a prezzo. Ride bene chi ride ultimo."
		expected = {}
		expected['word'] = [[u'Ogni', u'cosa', u'si', u'compra', u'a', u'prezzo', u'.'], [u'Ride', u'bene', u'chi', u'ride', u'ultimo', u'.']]
		expected['lemma'] = [[u'ogni', u'cosa', u'si', u'comprare', u'a', u'prezzo', u'.'], [u'ride', u'bene', u'chi', u'ridere', u'ultimare', u'.']]
		expected['partofspeech'] = [[u'DET', u'NOUN', u'PRON', u'VERB', u'ADP', u'NOUN', u'PUNCT'], [u'VERB', u'ADV', u'PRON', u'VERB', u'ADJ', u'PUNCT']]
		expected['startPos'] = [[0, 5, 10, 13, 20, 22, 28], [30, 35, 40, 44, 49, 55]]
		expected['endPos'] = [[4, 9, 12, 19, 21, 28, 29], [34, 39, 43, 48, 55, 56]]
		expected['dependencies'] = [[(1, 0, u'det'), (3, 1, u'obj'), (3, 2, u'expl'), (3, 3, u'ROOT'), (5, 4, u'case'), (3, 5, u'obl'), (3, 6, u'punct')], [(0, 0, u'ROOT'), (0, 1, u'advmod'), (0, 2, u'nsubj'), (2, 3, u'acl:relcl'), (3, 4, u'amod'), (0, 5, u'punct')]]

	elif language == 'pt':
		twoSentences = u"A caridade começa em casa. A experiência é mãe da ciência."
		expected = {}
		expected['word'] = [[u'A', u'caridade', u'come\xe7a', u'em', u'casa', u'.'], [u'A', u'experi\xeancia', u'\xe9', u'm\xe3e', u'da', u'ci\xeancia', u'.']]
		expected['lemma'] = [[u'a', u'caridade', u'comedir', u'em', u'casar', u'.'], [u'a', u'experi\xeancia', u'ser', u'm\xe3e', u'da', u'ci\xeancia', u'.']]
		expected['partofspeech'] = [[u'DET', u'NOUN', u'VERB', u'ADP', u'NOUN', u'PUNCT'], [u'DET', u'NOUN', u'VERB', u'NOUN', u'ADP', u'NOUN', u'PUNCT']]
		expected['startPos'] = [[0, 2, 11, 18, 21, 25], [27, 29, 41, 43, 47, 50, 57]]
		expected['endPos'] = [[1, 10, 17, 20, 25, 26], [28, 40, 42, 46, 49, 57, 58]]
		expected['dependencies'] = [[(1, 0, u'det'), (2, 1, u'nsubj'), (2, 2, u'ROOT'), (4, 3, u'case'), (2, 4, u'obl'), (2, 5, u'punct')], [(1, 0, u'det'), (3, 1, u'nsubj'), (3, 2, u'cop'), (3, 3, u'ROOT'), (5, 4, u'case'), (3, 5, u'nmod'), (3, 6, u'punct')]]

	elif language == 'nl':
		twoSentences = u"Zoals het klokje thuis tikt, tikt het nergens. Boontje komt om zijn loontje."
		expected = {}
		expected['word'] = [[u'Zoals', u'het', u'klokje', u'thuis', u'tikt', u',', u'tikt', u'het', u'nergens', u'.'], [u'Boontje', u'komt', u'om', u'zijn', u'loontje', u'.']]
		expected['lemma'] = [[u'zoals', u'het', u'klokje', u'thuis', u'tikt', u',', u'tikt', u'het', u'nergens', u'.'], [u'boontje', u'komt', u'om', u'zijn', u'loontje', u'.']]
		expected['partofspeech'] = [[u'CONJ', u'DET', u'NOUN', u'ADV', u'VERB', u'PUNCT', u'VERB', u'PRON', u'ADV', u'PUNCT'], [u'NOUN', u'VERB', u'ADP', u'PRON', u'NOUN', u'PUNCT']]
		expected['startPos'] = [[0, 6, 10, 17, 23, 27, 29, 34, 38, 45], [47, 55, 60, 63, 68, 75]]
		expected['endPos'] = [[5, 9, 16, 22, 27, 28, 33, 37, 45, 46], [54, 59, 62, 67, 75, 76]]
		expected['dependencies'] = [[(4, 0, u'mark'), (2, 1, u'det'), (4, 2, u'nsubj'), (4, 3, u'advmod'), (6, 4, u'advcl'), (6, 5, u'punct'), (6, 6, u'ROOT'), (6, 7, u'nsubj'), (6, 8, u'advmod'), (6, 9, u'punct')], [(1, 0, u'nsubj'), (1, 1, u'ROOT'), (4, 2, u'case'), (4, 3, u'nmod'), (1, 4, u'obj'), (1, 5, u'punct')]]

	return twoSentences,expected

def runLanguageTest(language,killCoreNLPIfNeeded,doDownloadIfNeeded):
	twoSentences,expected = getTestData(language)

	parser = kindred.Parser(language=language)
	corpus = kindred.Corpus(twoSentences)
	parser.parse(corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	assert len(doc.sentences) == 2


	letPass = False

	word = [ [ t.word for t in sentence.tokens ] for sentence in doc.sentences ]
	lemma = [ [ t.lemma for t in sentence.tokens ] for sentence in doc.sentences ]
	partofspeech = [ [ t.partofspeech for t in sentence.tokens ] for sentence in doc.sentences ]
	startPos = [ [ t.startPos for t in sentence.tokens ] for sentence in doc.sentences ]
	endPos = [ [ t.endPos for t in sentence.tokens ] for sentence in doc.sentences ]
	dependencies = [ sentence.dependencies for sentence in doc.sentences ]

	print("expected['word'] = %s" % str(word))
	print("expected['lemma'] = %s" % str(lemma))
	print("expected['partofspeech'] = %s" % str(partofspeech))
	print("expected['startPos'] = %s" % str(startPos))
	print("expected['endPos'] = %s" % str(endPos))
	print("expected['dependencies'] = %s" % str(dependencies))
	
	assert letPass or word == expected['word']
	assert letPass or lemma == expected['lemma']
	assert letPass or partofspeech == expected['partofspeech']
	assert letPass or startPos == expected['startPos']
	assert letPass or endPos == expected['endPos']
	assert letPass or dependencies == expected['dependencies']




def test_english():
	language = 'en'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=False)

def test_french():
	language = 'fr'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_german():
	language = 'de'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)
	
def test_spanish():
	language = 'es'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)
	
def test_portuguese():
	language = 'pt'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_italian():
	language = 'it'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)

def test_dutch():
	language = 'nl'
	runLanguageTest(language=language,killCoreNLPIfNeeded=True,doDownloadIfNeeded=True)
	


if __name__ == '__main__':
	test_portuguese()
	test_italian()
	test_dutch()

