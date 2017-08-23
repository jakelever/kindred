# -*- coding: utf-8 -*-

from kindred.pycorenlp import StanfordCoreNLP

import kindred
import json
from intervaltree import IntervalTree
from collections import defaultdict
from kindred.Dependencies import initializeCoreNLP,checkCoreNLPDownload

def shortenDepName(depName):
	acceptedSubNames = set(['acl:relcl','cc:preconj','compound:prt','det:predet','nmod:npmod','nmod:poss','nmod:tmod'])
	if depName in acceptedSubNames:
		return depName
	else:
	 	return depName.split(":")[0]

class Parser:
	"""
	Runs CoreNLP on corpus to get sentences and associated tokens
	"""
	
	def __init__(self,corenlp_url='http://localhost:9000',useConstituencyParserOnly=False,language='english'):
		"""
		Create a Parser object that will use CoreNLP for parsing
		
		:param corenlp_url: URL of the CoreNLP instance
		:param useConstituencyParserOnly: Use CoreNLP's constituency parser (with a conversion) for the depenency parse information, and not the CoreNLP dependency parser. This is slower
		:param language: Language to parse (english/arabic/chinese/french/german/spanish). The parser will check that the current CoreNLP is using the matching language. If not CoreNLP instance is running, it will launch one with the correct language.
		:type corenlp_url: str
		:type useConstituencyParserOnly: bool
		:type language: str
		"""

		acceptedLanguages = ['arabic','chinese','english','french','german','spanish']
		assert language in acceptedLanguages

		self.corenlp_url = corenlp_url

		if useConstituencyParserOnly:
			self.annotators = 'ssplit,tokenize,pos,lemma,parse'
		else:
			self.annotators = 'ssplit,tokenize,pos,lemma,depparse'

		self.nlp = StanfordCoreNLP(self.corenlp_url)
		self.language = language

	def _languageTest(self):
		testData = {}
		testData['arabic'] = {'text':u"أي ساعة؟ وقت العشاء.",'expectedPOS':[[u'NOUN', u'NN', u'PUNC'], [u'NN', u'DTNN', u'PUNC']]}
		testData['chinese'] = {'text':u"這種食物很好吃你最喜歡什麼？",'expectedPOS':[[u'NN', u'NN', u'AD', u'VA', u'PN', u'AD', u'VV', u'NN', u'PU']]}
		testData['english'] = {'text':'Of all the things I miss my mind the most. Colourless green ideas sleep furiously','expectedPOS':[[u'IN', u'PDT', u'DT', u'NNS', u'PRP', u'VBP', u'PRP$', u'NN', u'DT', u'JJS', u'.'], [u'JJ', u'JJ', u'NNS', u'VBP', u'RB']]}
		testData['french'] = {'text':"Ceci n'est pas une pipe. Ceci n'est pas une lune",'expectedPOS':[[u'PRO', u'ADV', u'V', u'ADV', u'DET', u'NC', u'PUNC'], [u'PRO', u'ADV', u'V', u'ADV', u'DET', u'NC']]}
		testData['german'] = {'text':u"Kümmere Dich nicht um ungelegte Eier. Morgenstund hat Gold im Mund.",'expectedPOS':[[u'ADJA', u'PPER', u'PTKNEG', u'APPR', u'ADJA', u'NN', u'$.'], [u'NE', u'VAFIN', u'NN', u'APPRART', u'NN', u'$.']]}
		testData['spanish'] = {'text':u"Si adelante no vas, altrasarás. Despues de los años mil, Torna el agua a su carril.",'expectedPOS':[[u'cs', u'rg', u'rn', u'vmip000', u'fc', u'rg', u'fp'], [u'rg', u'sp000', u'da0000', u'nc0p000', u'z0', u'fc', u'np00000', u'da0000', u'nc0s000', u'sp000', u'dp0000', u'nc0s000', u'fp']]}

		assert self.language in testData, "Cannot test language %s as no test data exists" % self.language

		parsed = self.nlp.annotate(testData[self.language]['text'], properties={'annotators': 'ssplit,tokenize,pos','outputFormat': 'json'})
		partsOfSpeech = [ [ token['pos'] for token in sentence['tokens'] ] for sentence in parsed['sentences'] ]
		if partsOfSpeech != testData[self.language]['expectedPOS']:
			raise RuntimeError("CoreNLP currently running does not match the language (%s) requested by the parser. Please stop this CoreNLP instance and either launch the appropriate one or let Kindred launch one." % self.language)

	def _testConnection(self):
		assert not self.nlp is None
	
		try:
			parsed = self.nlp.annotate("This is a test", properties={'annotators': self.annotators,'outputFormat': 'json'})
			
			assert not parsed is None

			return True
		except:
			return False

	def _setupConnection(self):
		#if not checkCoreNLPDownload():
		#	raise RuntimeError("Cannot access local CoreNLP at http://localhost:9000 and cannot find CoreNLP files to launch subprocess. Please download using kindred.downloadCoreNLP() if subprocess should be used")

		initializeCoreNLP(language=self.language)
		self.nlp = StanfordCoreNLP(self.corenlp_url)
			
		assert self._testConnection() == True

	def parse(self,corpus):
		"""
		Parse the corpus. Each document will be split into sentences which are then tokenized and parsed for their dependency graph. All parsed information is stored within the corpus object.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		"""

		assert isinstance(corpus,kindred.Corpus)

		if self._testConnection() == False:
			self._setupConnection()

		self._languageTest()
		
		for d in corpus.documents:
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					denotationTree[a:b] = e.entityID
				
			parsed = self.nlp.annotate(d.getText(), properties={'annotators': self.annotators,'outputFormat': 'json'})

			for sentence in parsed["sentences"]:
				#assert False
				tokens = []
				for t in sentence["tokens"]:
					#kindred.Token(token,pos,lemma,start,end)
					token = kindred.Token(t["word"],t["lemma"],t["pos"],t["characterOffsetBegin"],t["characterOffsetEnd"])
					tokens.append(token)

				dependencies = []
				for de in sentence["enhancedPlusPlusDependencies"]:
				#for de in sentence["collapsed-ccprocessed-dependencies"]:
					#depName = de["dep"].split(":")[0]
					depName = shortenDepName(de["dep"])
					#if depName == 'nmod:in_addition_to':
					#	assert False
					dep = (de["governor"]-1,de["dependent"]-1,depName)
					dependencies.append(dep)
				# TODO: Should I filter this more or just leave it for simplicity
					
				entityIDsToTokenLocs = defaultdict(list)
				for i,t in enumerate(tokens):
					entitiesOverlappingWithToken = denotationTree[t.startPos:t.endPos]
					for interval in entitiesOverlappingWithToken:
						entityID = interval.data
						entityIDsToTokenLocs[entityID].append(i)

				# Let's gather up the information about the "known" entities in the sentence
				entitiesWithLocations = []
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					e = entityIDsToEntities[entityID]
					entityWithLocation = (e, entityLocs)
					entitiesWithLocations.append(entityWithLocation)
					
				sentence = kindred.Sentence(tokens, dependencies, entitiesWithLocations, d.getSourceFilename())
				d.addSentence(sentence)

		corpus.parsed = True

