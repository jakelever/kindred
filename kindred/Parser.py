
import json

from kindred.pycorenlp import StanfordCoreNLP

import kindred
from intervaltree import Interval, IntervalTree
from collections import defaultdict
from kindred.Dependencies import initializeCoreNLP,checkCoreNLPDownload,testCoreNLPConnection

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
		self.corenlp_url = corenlp_url

	nlp = None

	def testConnection(self):
		if Parser.nlp is None:
			return False
	
		try:
			parsed = Parser.nlp.annotate("This is a test", properties={'annotators': 'tokenize,ssplit,lemma,pos,depparse,parse','outputFormat': 'json'})
			return True
		except:
			return False

	def setupConnection(self):
		if not checkCoreNLPDownload():
			raise RuntimeError("Cannot access local CoreNLP at http://localhost:9000 and cannot find CoreNLP files to launch subprocess. Please download using kindred.downloadCoreNLP() if subprocess should be used")

		initializeCoreNLP()
		Parser.nlp = StanfordCoreNLP(self.corenlp_url)
			
		assert self.testConnection() == True

	def parse(self,corpus):
		assert isinstance(corpus,kindred.Corpus)

		if self.testConnection() == False:
			self.setupConnection()
		
		for d in corpus.documents:
			entityIDsToEntities = d.getEntityIDsToEntities()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.position:
					denotationTree[a:b] = e.entityID
				
			parsed = Parser.nlp.annotate(d.getText(), properties={'annotators': 'tokenize,ssplit,lemma,pos,depparse,parse','outputFormat': 'json'})
	
			

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
					entityType = entityTypeLookup[entityID]
					e = entityIDsToEntities[entityID]
					entityWithLocation = (e, entityLocs)
					entitiesWithLocations.append(entityWithLocation)
					
				sentence = kindred.Sentence(tokens, dependencies, entitiesWithLocations, d.getSourceFilename())
				d.addSentence(sentence)

		corpus.parsed = True

