
import json

from kindred.pycorenlp import StanfordCoreNLP

import kindred
from intervaltree import Interval, IntervalTree
from collections import defaultdict
from kindred.Dependencies import initializeCoreNLP,checkCoreNLPDownload

def shortenDepName(depName):
	acceptedSubNames = set(['acl:relcl','cc:preconj','compound:prt','det:predet','nmod:npmod','nmod:poss','nmod:tmod'])
	if depName in acceptedSubNames:
		return depName
	else:
	 	return depName.split(":")[0]

class Parser:
	def __init__(self):
		pass

	nlp = None

	def parse(self,corpus):
		assert isinstance(corpus,kindred.Corpus)

		if Parser.nlp is None:
			try:
				Parser.nlp = StanfordCoreNLP('http://localhost:9000')
				parsed = Parser.nlp.annotate("This is a test", properties={'annotators': 'tokenize,ssplit,lemma,pos,depparse,parse','outputFormat': 'json'})
			except:
				if checkCoreNLPDownload():
					initializeCoreNLP()
					Parser.nlp = StanfordCoreNLP('http://localhost:9000')
				else:
				 	raise RuntimeError("Cannot access local CoreNLP at http://localhost:9000 and cannot find CoreNLP files to launch subprocess. Please download using kindred.downloadCoreNLP() if subprocess should be used")
				
		
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
				processedEntities = []
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					entityType = entityTypeLookup[entityID]
					e = entityIDsToEntities[entityID]
					processedEntity = kindred.ProcessedEntity(e.entityType,entityLocs,entityID,e.sourceEntityID,e.position,e.text)
					processedEntities.append(processedEntity)
					
				relations = []
				# Let's also put in the relation information if we can get it
				if isinstance(d,kindred.Document):
					tmpRelations = d.getRelations()
					entitiesInSentence = entityIDsToTokenLocs.keys()
					for tmpRelation in tmpRelations:
						matched = [ (relationEntityID in entitiesInSentence) for relationEntityID in tmpRelation.entityIDs ]
						if all(matched):
							relations.append(tmpRelation)
					
				sentence = kindred.ProcessedSentence(tokens, dependencies, processedEntities, relations, d.getSourceFilename())
				d.addProcessedSentence(sentence)
	
	#return allSentenceData
