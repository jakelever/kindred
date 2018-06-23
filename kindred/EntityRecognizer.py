import sys
import itertools
import kindred
import pickle
import argparse
import codecs
import time
import re
import string
from collections import defaultdict,Counter
import json
import six
import os

def acronymMatch(words,pos,currentAcronym,atStart,subpos=None):
	if len(currentAcronym) == 0:
		if not (subpos is None): # Can't finish acronym mid-word
			return []
		else:
			return [pos+1]

	curWord = words[pos].lower()
	wordSplit = curWord.split('-')
	curLetter = currentAcronym[-1]
	
	moves = []
	
	if subpos is None:
		if atStart and curLetter == 's' and curWord[-1] == 's':
			# Possible plural
			moves.append( (words,pos,currentAcronym[:-1],False) )
			
		if curLetter == curWord[0]:
			moves.append( (words,pos-1,currentAcronym[:-1],False) )

		if curWord == '-':
			moves.append( (words,pos-1,currentAcronym,False) )
			

	if len(wordSplit) > 1:
		if subpos is None:
			subpos = len(wordSplit)-1
		if len(wordSplit[subpos]) > 0 and curLetter == wordSplit[subpos][0]:
			if subpos == 0:
				moves.append( (words,pos-1,currentAcronym[:-1],False) )
			else:
				moves.append( (words,pos,currentAcronym[:-1],False,subpos-1) )
			
	possibleStarts = []
	for move in moves:
		possibleStarts += acronymMatch(*move)
		
	return possibleStarts

def acronymDetection(words):
	LRBs = [i for i, x in enumerate(words) if x == u'(']
	RRBs = [i for i, x in enumerate(words) if x == u')']
	acronyms = []
	for i,j in itertools.product(LRBs,RRBs):
		if j-i == 2:
			acronymLoc = i+1
			possibleAcronym = words[acronymLoc]
			possibleStarts = acronymMatch(words,i-1,possibleAcronym.lower(),True)
			if len(possibleStarts) > 0:
				start = min(possibleStarts)
				end = i
				acronyms.append((start,end,acronymLoc))
	return acronyms

def mergeWordsForFusionDetection(words):
	prevWord = ""
	mergedWords = []
	start = 0
	mergeChars = ['-','/',':']
	for i,w in enumerate(words):
		if w in mergeChars:
			prevWord += w
		elif len(prevWord) > 0 and prevWord[-1] in mergeChars:
			prevWord += w
		else:
			if prevWord:
				mergedWords.append((start,i-1,prevWord))
			prevWord = w
			start = i

	if prevWord:
		mergedWords.append((start,len(words)-1,prevWord))

	return mergedWords

def fusionGeneDetection(words, lookupDict):
	termtypesAndids,terms,locs = [],[],[]
	origWords = list(words)
	words = [ w.lower() for w in words ]

	mergedWords = mergeWordsForFusionDetection(words)

	for start,end,word in mergedWords:
		split = re.split("[-/:]",word)
		fusionCount = len(split)
		if fusionCount == 1:
			continue
			
		allGenes = True
		
		geneIDs = []
		lookupIDCounter = Counter()
		for s in split:
			key = (s,)
			if key in lookupDict:
				isGene = False
				for entityType,entityID in lookupDict[key]:
					if entityType == 'gene':
						for tmpID in entityID.split(';'):
							lookupIDCounter[tmpID] += 1

						geneIDs.append(entityID)
						isGene = True
						break
				if not isGene:
					allGenes = False
					break
			else:
				allGenes = False
				break

		# We're going to check if there are any lookup IDs shared among all the "fusion" terms
		# Hence this may not actually be a fusion, but just using multiple names of a gene
		# e.g. HER2/neu
		completeLookupIDs = [ id for id,count in lookupIDCounter.items() if count == fusionCount ]
		if len(completeLookupIDs) > 0:
			termtypesAndids.append([('gene',';'.join(completeLookupIDs))])
			terms.append(tuple(origWords[start:end+1]))
			locs.append((start,end+1))
		elif allGenes: # All the terms look like genes (and different genes), so we're going to mark this as a fusion (or combo)
			#geneTxt = ",".join(map(str,geneIDs))
			geneIDs = [ geneID.replace(';','&') for geneID in geneIDs ]
			termtypesAndids.append([('gene','combo|' + '|'.join(geneIDs))])
			terms.append(tuple(origWords[start:end+1]))
			locs.append((start,end+1))
		
	return locs,terms,termtypesAndids

def getTermIDsAndLocations(np, lookupDict):
	termtypesAndids,terms,locs = [],[],[]
	# Lowercase all the tokens
	#np = [ unicodeLower(w) for w in np ]
	orignp = np
	np = [ w.lower() for w in np ]

	# The length of each search string will decrease from the full length
	# of the text down to 1
	for l in reversed(range(1, len(np)+1)):
		# We move the search window through the text
		for i in range(len(np)-l+1):
			# Extract that window of text
			s = tuple(np[i:i+l])
			# Search for it in the dictionary
			if s in lookupDict:
				# If found, save the ID(s) in the dictionary
				termtypesAndids.append(lookupDict[s])
				terms.append(tuple(orignp[i:i+l]))
				locs.append((i,i+l))
				# And blank it out
				np[i:i+l] = [ "" for _ in range(l) ]

	# Then return the found term IDs
	return locs,terms,termtypesAndids

def startsWithButNotAll(s,search):
	return s.startswith(search) and len(s) > len(search)

def cleanupVariant(variant):
	variant = variant.upper().replace('P.','')
	aminoAcidInfo = [('ALA','A'),('ARG','R'),('ASN','N'),('ASP','D'),('CYS','C'),('GLU','E'),('GLN','Q'),('GLY','G'),('HIS','H'),('ILE','I'),('LEU','L'),('LYS','K'),('MET','M'),('PHE','F'),('PRO','P'),('SER','S'),('THR','T'),('TRP','W'),('TYR','Y'),('VAL','V')]
	for longA,shortA in aminoAcidInfo:
		variant = variant.replace(longA,shortA)
	return variant

class EntityRecognizer:
	def __init__(self,lookup,detectFusionGenes=False,detectMicroRNA=False,acronymDetectionForAmbiguity=False,mergeTerms=False,detectVariants=False,variantStopwords=[],detectPolymorphisms=False,removePathways=False):
		"""
		Create an EntityRecognizer and provide the lookup table for terms and additional flags for what to identify in text

		:param lookup: A dictionary of terms (tuple of parsed words) to a list of (entityType,externalID).
		:param detectFusionGenes: Whether to try to identify fusion gene terms (e.g. BCR-ABL1). Lookup must contain terms of type 'gene'
		:param detectMicroRNA: Whether to identify microRNA terms (added as 'gene' entities)
		:param acronymDetectionForAmbiguity: Whether to try to identify acronyms and use this to deal with ambiguity (by removing incorrect matches to acronyms or the longer terms)
		:param mergeTerms: Whether to merge neighbouring terms that refer to the same external entity (e.g. HER2/neu as one term instead of two)
		:param detectVariants: Whether to identify a variant (e.g. V600E) and create an entity of type 'Mutation'
		:param variantStopwords: Variant terms to be ignored (e.g. S100P) if detectVariants is used
		:param detectPolymorphisms: Whether to identify a SNP (using a dbSNP ID) and create an entity of type 'Mutation'
		:param removePathways: Remove genes that are actually naming a signalling pathway (e.g. MTOR pathway)
		:type lookup: dict
		:type detectFusionGenes: bool
		:type detectMicroRNA: bool
		:type acronymDetectionForAmbiguity: bool
		:type mergeTerms: bool
		:type detectVariants: bool
		:type variantStopwords: list
		:type detectPolymorphisms: bool
		:type removePathways: bool
		"""

		assert isinstance(lookup,dict)
		for termsmatch,typeAndIDs in lookup.items():
			assert isinstance(termsmatch,tuple), "Lookup key must be a tuple of strings"
			assert isinstance(typeAndIDs,set), "Lookup value must be a list of (entityType,externalID)"
			assert len(typeAndIDs)>0, "Lookup value must be a list of (entityType,externalID)"
			for typeAndID in typeAndIDs:
				assert isinstance(typeAndID,tuple),"Lookup value must be a list of (entityType,externalID)"
				assert len(typeAndID)==2, "Lookup value must be a list of (entityType,externalID)"

		assert isinstance(detectFusionGenes,bool)
		assert isinstance(detectMicroRNA,bool)
		assert isinstance(acronymDetectionForAmbiguity,bool)
		assert isinstance(mergeTerms,bool)
		assert isinstance(detectVariants,bool)
		assert isinstance(detectPolymorphisms,bool)
		
		assert isinstance(variantStopwords,list)
		for variantStopword in variantStopwords:
			assert isinstance(variantStopword,six.string_types), "variantStopwords should be a list of strings"

		self.lookup = lookup
		self.detectFusionGenes = detectFusionGenes
		self.detectMicroRNA = detectMicroRNA
		self.acronymDetectionForAmbiguity = acronymDetectionForAmbiguity
		self.mergeTerms = mergeTerms
		self.detectVariants = detectVariants
		self.variantStopwords = set(variantStopwords)
		self.detectPolymorphisms = detectPolymorphisms
		self.removePathways = removePathways

		
	def _processWords(self, words):
		locs,terms,termtypesAndids = getTermIDsAndLocations(words,self.lookup)

		if self.detectVariants:
			#snvRegex = r'^[A-Z][0-9]+[A-Z]$'
			variantRegex1 = r'^[ACDEFGHIKLMNPQRSTVWY][1-9][0-9]*[ACDEFGHIKLMNPQRSTVWY]$'
			variantRegex2 = r'^(p\.)?((Ala)|(Arg)|(Asn)|(Asp)|(Cys)|(Glu)|(Gln)|(Gly)|(His)|(Ile)|(Leu)|(Lys)|(Met)|(Phe)|(Pro)|(Ser)|(Thr)|(Trp)|(Tyr)|(Val))[1-9][0-9]*((Ala)|(Arg)|(Asn)|(Asp)|(Cys)|(Glu)|(Gln)|(Gly)|(His)|(Ile)|(Leu)|(Lys)|(Met)|(Phe)|(Pro)|(Ser)|(Thr)|(Trp)|(Tyr)|(Val))$'

			filteredWords = [ w for w in words if not w in self.variantStopwords ]
			snvMatches1 = [ not (re.match(variantRegex1,w) is None) for w in filteredWords ]
			snvMatches2 = [ not (re.match(variantRegex2,w,re.IGNORECASE) is None) for w in filteredWords ]

			snvMatches = [ (match1 or match2) for match1,match2 in zip(snvMatches1,snvMatches2) ]
			for i,(w,snvMatch) in enumerate(zip(words,snvMatches)):
				if snvMatch:
					cleaned = cleanupVariant(w)
					potentialLocs = (i,i+1)
					if not potentialLocs in locs:
						termtypesAndids.append([('variant',"substitution|%s"%cleaned)])
						terms.append((w,))
						locs.append(potentialLocs)

		if self.detectPolymorphisms:
			polymorphismRegex1 = r'^rs[1-9][0-9]*$'

			polyMatches = [ not (re.match(polymorphismRegex1,w) is None) for w in words ]

			for i,(w,polyMatch) in enumerate(zip(words,polyMatches)):
				if polyMatch:
					potentialLocs = (i,i+1)
					if not potentialLocs in locs:
						termtypesAndids.append([('variant','dbsnp|%s'%w)])
						terms.append((w,))
						locs.append(potentialLocs)

		if self.detectMicroRNA:
			for i,w in enumerate(words):
				lw = w.lower()
				if startsWithButNotAll(lw,"mir-") or startsWithButNotAll(lw,"hsa-mir-") or startsWithButNotAll(lw,"microrna-") or (startsWithButNotAll(lw,"mir") and lw[3] in string.digits):
					potentialLocs = (i,i+1)
					if not potentialLocs in locs:
						termtypesAndids.append([('gene','mirna|'+w)])
						terms.append((w,))
						locs.append((i,i+1))

		toRemove = []
		if self.detectFusionGenes:
			fusionLocs,fusionTerms,fusionTermtypesAndids = fusionGeneDetection(words,self.lookup)
	
			for floc,fterm,ftermtypesAndid in zip(fusionLocs,fusionTerms,fusionTermtypesAndids):
				if not floc in locs:
					# Check for which entities to remove that are inside this fusion term
					fstart,fend = floc
					for tstart,tend in locs:
						if fstart <= tstart and tend <= fend:
							toRemove.append((tstart,tend))

					locs.append(floc)
					terms.append(fterm)
					termtypesAndids.append(ftermtypesAndid)

		filtered = zip(locs,terms,termtypesAndids)
		filtered = [ (l,t,ti) for l,t,ti in filtered if not l in toRemove ]
		filtered = sorted(filtered)

		if self.mergeTerms:
			# We'll attempt to merge terms (i.e. if a gene is referred to using two acronyms together)
			# Example: Hepatocellular carcinoma (HCC) or HER2/ Neu or INK4B P15
			locsToRemove = set()
			for i in range(len(filtered)-1):
				(startA,endA),termsA,termTypesAndIDsA = filtered[i]
				(startB,endB),termsB,termTypesAndIDsB = filtered[i+1]
				
				# Check that the terms are beside each other or separated by a /,- or (
				if startB == endA or (startB == (endA+1) and words[endA] in ['/','-','(',')']):
					idsA,idsB = set(),set()

					for termType, termIDs in termTypesAndIDsA:
						for termID in termIDs.split(';'):
							idsA.add((termType,termID))
					for termType, termIDs in termTypesAndIDsB:
						for termID in termIDs.split(';'):
							idsB.add((termType,termID))

					idsIntersection = idsA.intersection(idsB)

					# Detect if the either term is in brackets e.g. HER2 (ERBB2)
					firstTermInBrackets,secondTermInBrackets = False,False
					if startB == (endA+1) and endB < len(words) and words[endA] == '(' and words[endB] == ')':
						secondTermInBrackets = True
					if startB == (endA+1) and startA > 0 and words[startA-1] == '(' and words[endA] == ')':
						firstTermInBrackets = True

					# The two terms share IDs so we're going to merge them
					idsShared = (len(idsIntersection) > 0)

					if idsShared:
						groupedByType = defaultdict(list)
						for termType,termID in idsIntersection:
							groupedByType[termType].append(termID)

						locsToRemove.add((startA,endA))
						locsToRemove.add((startB,endB))

						if secondTermInBrackets:
							thisLocs = (startA,endB+1)
							thisTerms = tuple(words[startA:endB+1])
						elif firstTermInBrackets:
							thisLocs = (startA-1,endB)
							thisTerms = tuple(words[startA-1:endB])
						else:
							thisLocs = (startA,endB)
							thisTerms = tuple(words[startA:endB])


						thisTermTypesAndIDs = [ (termType,";".join(sorted(termIDs))) for termType,termIDs in groupedByType.items() ]

						filtered.append((thisLocs,thisTerms,thisTermTypesAndIDs))

			# Now we have to remove the terms marked for deletion in the previous section
			filtered = [ (locs,terms,termtypesAndids) for locs,terms,termtypesAndids in filtered if not locs in locsToRemove]
			filtered = sorted(filtered)

		if self.acronymDetectionForAmbiguity:
			# And we'll check to see if there are any obvious acronyms
			locsToRemove = set()
			acronyms = acronymDetection(words)
			for (wordsStart,wordsEnd,acronymLoc) in acronyms:
				wordIsTerm = (wordsStart,wordsEnd) in locs
				acronymIsTerm = (acronymLoc,acronymLoc+1) in locs
				
				if wordIsTerm and acronymIsTerm:
					# Remove the acronym
					locsToRemove.add((acronymLoc,acronymLoc+1))
				elif acronymIsTerm:
					# Remove any terms that contain part of the spelt out word
					newLocsToRemove = [ (i,j) for i in range(wordsStart,wordsEnd) for j in range(i,wordsEnd+1) ]
					locsToRemove.update(newLocsToRemove)
				

			# Now we have to remove the terms marked for deletion in the previous section
			filtered = [ (locs,terms,termtypesAndids) for locs,terms,termtypesAndids in filtered if not locs in locsToRemove]
			filtered = sorted(filtered)

		if self.removePathways:
			forbiddenPathwayWords = set(['pathway','pathways','signaling','signalling','cascade'])
			filtered2 = []
			for locs,terms,termtypesAndids in filtered:
				nextTokenIndex = locs[1]
				nextTokenIsForbiddenWord = nextTokenIndex < len(words) and words[nextTokenIndex].lower() in forbiddenPathwayWords
				if nextTokenIsForbiddenWord:
					termtypesAndids = [ (termtype,termid) for termtype,termid in termtypesAndids if not termtype == 'gene' ]
				if len(termtypesAndids) > 0:
					filtered2.append((locs,terms,termtypesAndids))

			filtered = filtered2
		
		return filtered

	def annotate(self,corpus):
		"""
		Annotate a parsed corpus with the wordlist lookup and other entity types

		:param corpus: Corpus to annotate
		:type corpus: kindred.Corpus
		"""

		assert corpus.parsed == True, "Corpus must already be parsed before entity recognition"

		for doc in corpus.documents:
			for sentence in doc.sentences:
				words = [ t.word for t in sentence.tokens ]

				extractedTermData = self._processWords(words)
				
				for locs,terms,termtypesAndids in extractedTermData:
					#text = " ".join(terms)
					startToken = locs[0]
					endToken = locs[1]
					startPos = sentence.tokens[startToken].startPos
					endPos = sentence.tokens[endToken-1].endPos
					text = doc.text[startPos:endPos]
					loc = list(range(startToken,endToken))
					for entityType,externalID in termtypesAndids:
						e = kindred.Entity(entityType,text,[(startPos,endPos)],externalID=externalID)
						doc.addEntity(e)
						sentence.addEntityAnnotation(e,loc)

	@staticmethod
	def loadWordlists(entityTypesWithFilenames, idColumn=0, termsColumn=1, columnSeparator='\t', termSeparator='|'):
		"""
		Load a wordlist from multiple files. By default, each file should be a tab-delimited file with the first column is the ID and the second column containing all the terms separated by '|'. This can be modified by the parameters.

		As each term is parsed, this can take a long time. It is recommended to run this one time and save the output as a Python pickle file and load in.

		:param entityTypesWithFilenames: Dictionary of entityType => filename
		:param idColumn: The column containing the ID for the term (starts from 0)
		:param termsColumn: The column containing the list of terms (starts from 0)
		:param columnSeparator: The column separator for the file (default is a tab)
		:param termSeparator: The separator for the list of terms (default is a '|')
		:type entityTypesWithFilenames: dict
		:type idColumn: int
		:type termsColumn: int
		:type columnSeparator: str
		:type termSeparator: str
		:return: Dictionary of lookup values
		:rtype: dict
		"""
		errorMsg = 'entityTypesWithFilenames should be a dictionary with pairs of {entityType: filename} where both are strings and the filename points to a file that exists'
		assert isinstance(entityTypesWithFilenames,dict), errorMsg
		for entityType,filename in entityTypesWithFilenames.items():
			assert isinstance(entityType,six.string_types), errorMsg
			assert isinstance(filename,six.string_types), errorMsg
			assert os.path.isfile(filename), "%s does not exist" % filename

		assert isinstance(idColumn,int)
		assert isinstance(termsColumn,int)
		assert isinstance(columnSeparator,str)
		assert isinstance(termSeparator,str)

		import spacy
		nlp = spacy.load('en')

		requiredColumns = max(idColumn,termsColumn)+1

		lookup = defaultdict(set)
		for entityType,filename in entityTypesWithFilenames.items():
			with codecs.open(filename,'r','utf-8') as f:
				tempLookup = defaultdict(set)
				for lineno,line in enumerate(f):
					split = line.strip().split(columnSeparator)
					assert len(split) >= requiredColumns, 'Line %d contains only %d columns when %d are required' % (lineno+1,len(split),requiredColumns)
					termid,terms = split[idColumn],split[termsColumn]
					for term in terms.split(termSeparator):
						tupleterm = tuple([ token.text.strip().lower() for token in nlp(term) ])
						tempLookup[tupleterm].add(termid)

			for tupleterm,idlist in tempLookup.items():
				lookup[tupleterm].add( (entityType,";".join(sorted(list(idlist)))) )

		return dict(lookup)

