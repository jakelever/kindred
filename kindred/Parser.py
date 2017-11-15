# -*- coding: utf-8 -*-

import spacy
import kindred
from intervaltree import IntervalTree
from collections import defaultdict

class Parser:
	"""
	Runs CoreNLP on corpus to get sentences and associated tokens
	"""
	
	def __init__(self,corenlp_url=None,useConstituencyParserOnly=False,language='english'):
		"""
		Create a Parser object that will use CoreNLP for parsing
		
		:param corenlp_url: URL of the CoreNLP instance
		:param useConstituencyParserOnly: Use CoreNLP's constituency parser (with a conversion) for the depenency parse information, and not the CoreNLP dependency parser. This is slower
		:param language: Language to parse (english/arabic/chinese/french/german/spanish). The parser will check that the current CoreNLP is using the matching language. If no CoreNLP instance is running, it will launch one with the correct language.
		:type corenlp_url: str
		:type useConstituencyParserOnly: bool
		:type language: str
		"""

		acceptedLanguages = ['arabic','chinese','english','french','german','spanish']
		assert language in acceptedLanguages

		self.corenlp_url = corenlp_url

		self.language = language

		self.nlp = spacy.load('en', disable=['ner'])

	def _sentencesGenerator(self,text):
		parsed = self.nlp(text)
		sentence = None
		for token in parsed:
			if sentence is None or token.is_sent_start:
				if not sentence is None:
					yield sentence
				sentence = []
			sentence.append(token)

		if not sentence is None and len(sentence) > 0:
			yield sentence

	def sentenceSplit(docTokens):
		result = []
		sentence = []
		#for token in parsed:
		for token in docTokens:
			if token.is_sent_start:
				result.append(sentence)
				sentence = []
			sentence.append(token)

		if len(sentence) > 0:
			result.append(sentence)

		return sentenceSplit

	def parse(self,corpus):
		"""
		Parse the corpus. Each document will be split into sentences which are then tokenized and parsed for their dependency graph. All parsed information is stored within the corpus object.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		"""

		assert isinstance(corpus,kindred.Corpus)

		for d in corpus.documents:
		#for doctokens in self.nlp.pipe( d.text for d in corpus.documents, batch_size=2, n_threads=1):
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					denotationTree[a:b] = e.entityID
				
			for sentence in self._sentencesGenerator(d.text):
				tokens = []
				for t in sentence:
					token = kindred.Token(t.text,t.lemma_,t.pos_,t.idx,t.idx+len(t.text))
					tokens.append(token)

				sentenceStart = tokens[0].startPos
				sentenceEnd = tokens[-1].endPos
				sentenceTxt = d.text[sentenceStart:sentenceEnd]

				indexOffset = sentence[0].i
				dependencies = []
				for t in sentence:
					depName = t.dep_
					dep = (t.head.i-indexOffset,t.i-indexOffset,depName)
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
					
				sentence = kindred.Sentence(sentenceTxt, tokens, dependencies, entitiesWithLocations, d.getSourceFilename())
				d.addSentence(sentence)

		corpus.parsed = True

