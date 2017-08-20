
from kindred.pycorenlp import StanfordCoreNLP

import kindred
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
	
	def __init__(self,corenlp_url='http://localhost:9000'):
		"""
		Create a Parser object that will use CoreNLP for parsing
		
		:param corenlp_url: URL of the CoreNLP instance
		:type corenlp_url: str
		"""

		self.corenlp_url = corenlp_url

	_nlp = None

	_annotators = 'tokenize,ssplit,lemma,pos,depparse,parse'

	def _testConnection(self):
		if Parser._nlp is None:
			return False
	
		try:
			parsed = Parser._nlp.annotate("This is a test", properties={'annotators': Parser._annotators,'outputFormat': 'json'})
			
			assert not parsed is None

			return True
		except:
			return False

	def _setupConnection(self):
		if not checkCoreNLPDownload():
			raise RuntimeError("Cannot access local CoreNLP at http://localhost:9000 and cannot find CoreNLP files to launch subprocess. Please download using kindred.downloadCoreNLP() if subprocess should be used")

		initializeCoreNLP()
		Parser._nlp = StanfordCoreNLP(self.corenlp_url)
			
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
		
		for d in corpus.documents:
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					denotationTree[a:b] = e.entityID
				
			parsed = Parser._nlp.annotate(d.getText(), properties={'annotators': Parser._annotators,'outputFormat': 'json'})
	
			

			for sentence in parsed["sentences"]:
				#assert False
				tokens = []
				for t in sentence["tokens"]:
					#kindred.Token(token,pos,lemma,start,end)
					token = kindred.Token(t["word"],t["pos"],t["lemma"],t["characterOffsetBegin"],t["characterOffsetEnd"])
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

