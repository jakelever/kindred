# -*- coding: utf-8 -*-


import kindred
from intervaltree import IntervalTree
from collections import defaultdict
import six

class Parser:
	"""
	Runs Spacy on corpus to get sentences and associated tokens
	"""

	languageModels = {}
	
	def __init__(self,language='en'):
		"""
		Create a Parser object that will use Spacy for parsing. It offers all the same languages that Spacy offers. Check out: https://spacy.io/usage/models. Note that the language model needs to be downloaded first (e.g. python -m spacy download en)
		
		:param language: Language to parse (en/de/es/pt/fr/it/nl)
		:type language: str
		"""

		# We only load spacy if a Parser is created (to allow ReadTheDocs to build the documentation easily)
		import spacy

		acceptedLanguages = ['en','de','es','pt','fr','it','nl']
		assert language in acceptedLanguages, "Language for parser (%s) not in accepted languages: %s" % (language,str(acceptedLanguages))

		self.language = language

		if not language in Parser.languageModels:
			Parser.languageModels[language] = spacy.load(language, disable=['ner'])

		self.nlp = Parser.languageModels[language]

	def _sentencesGenerator(self,text):
		if six.PY2 and isinstance(text,str):
			text = unicode(text)

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

	def parse(self,corpus):
		"""
		Parse the corpus. Each document will be split into sentences which are then tokenized and parsed for their dependency graph. All parsed information is stored within the corpus object.
		
		:param corpus: Corpus to parse
		:type corpus: kindred.Corpus
		"""

		assert isinstance(corpus,kindred.Corpus)

		# Ignore DeprecationWarning from SortedDict which is inside IntervalTree
		import warnings
		warnings.filterwarnings("ignore", category=DeprecationWarning)

		for d in corpus.documents:
			entityIDsToEntities = { entity.entityID:entity for entity in d.entities }
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.entities:
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					if b > a:
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

				entityIDsToTokenLocs = defaultdict(list)
				for i,t in enumerate(tokens):
					entitiesOverlappingWithToken = denotationTree[t.startPos:t.endPos]
					for interval in entitiesOverlappingWithToken:
						entityID = interval.data
						entityIDsToTokenLocs[entityID].append(i)

				sentence = kindred.Sentence(sentenceTxt, tokens, dependencies, d.sourceFilename)
				
				# Let's gather up the information about the "known" entities in the sentence
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					# Get the entity associated with this ID
					e = entityIDsToEntities[entityID]
					sentence.addEntityAnnotation(e,entityLocs)
					
				d.addSentence(sentence)

		corpus.parsed = True

