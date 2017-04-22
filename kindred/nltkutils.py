#import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize, pos_tag,download

import sys

from nltk.corpus import wordnet as wn
import kindred
from nltk.parse.util import taggedsents_to_conll
from nltk.parse.stanford import StanfordDependencyParser
#from nltk.parse.malt import MaltParser
from kindred.Dependencies import getMaltParser

from kindred import Dependencies

nltkPackagesOkay = False
def checkNLTKPackages():
	global nltkPackagesOkay
	if not nltkPackagesOkay:
		print "Starting download check"
		requiredPackages = ['wordnet','punkt','averaged_perceptron_tagger']
		for package in requiredPackages:
			download(package,quiet=True)
		nltkPackagesOkay = True
		print "Finishing download check"

def is_noun(tag):
    return tag in ['NN', 'NNS', 'NNP', 'NNPS']


def is_verb(tag):
    return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def is_adverb(tag):
    return tag in ['RB', 'RBR', 'RBS']


def is_adjective(tag):
    return tag in ['JJ', 'JJR', 'JJS']


def penn_to_wn(tag):
	if is_adjective(tag):
		return wn.ADJ
	elif is_noun(tag):
		return wn.NOUN
	elif is_adverb(tag):
		return wn.ADV
	elif is_verb(tag):
		return wn.VERB
	return None
	
wordnet_lemmatizer = None
maltparser = None
stanfordparser = None
#@profile
def parseSentences(text,depparserOption='stanford'):
	if sys.version_info >= (3, 0):
		assert isinstance(text,str), relationErrorMsg
	else:
		assert isinstance(text,basestring), relationErrorMsg
	assert depparserOption == 'stanford' or depparserOption == 'malt'

	global wordnet_lemmatizer
	global maltparser,stanfordparser
	
	checkNLTKPackages()
	
	if wordnet_lemmatizer is None:
		wordnet_lemmatizer = WordNetLemmatizer()
		
	if depparserOption == 'stanford':
		if stanfordparser is None:
			Dependencies.initializeStanfordParser()
			stanfordparser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
		depparser = stanfordparser
	elif depparserOption == 'malt':
		if maltparser is None:
			maltparser = getMaltParser()
		depparser = maltparser

	#TODO: Deal with Unicode issues gracefully in Python2/3
	text = text.encode('ascii','ignore')
		

	sentences = sent_tokenize(text)
	tokenSets = [ word_tokenize(s) for s in sentences ]
		
	depparser_result = depparser.parse_sents(tokenSets)
	
	depparses = []
	for d in depparser_result:
		d = list(d)
		assert len(d) == 1, "Expected parser to return a single parse"
		depparses.append(d[0])
		
	output = []
		
	currentSentencePos = 0
	for sentence,tokens,depparse in zip(sentences,tokenSets,depparses):
		sentenceStartPos = text.find(sentence,currentSentencePos)
		assert sentenceStartPos != '-1', "Couldn't find location of sentence in text"
		currentSentencePos = sentenceStartPos + len(sentence)
			
		tokensAndPOS = pos_tag(tokens)
		wordnetTypes = [ penn_to_wn(pos) for token,pos in tokensAndPOS ]
		lemmas = [ token if wnpos is None else wordnet_lemmatizer.lemmatize(token,pos=wnpos) for (token,pos),wnpos in zip(tokensAndPOS,wordnetTypes) ]
		#lemmas = [ t for t,_ in tokensAndPOS ]

		substitutions = { '``': '"', "''": '"' }
		
		currentTokenPosition = 0
		locs = []
		for t,_ in tokensAndPOS:
		
			# Deal with special characters output by parser
			if t in substitutions:
				t = substitutions[t]
				
			start = sentence.find(t,currentTokenPosition)
			assert start != -1, "Error finding token: %s in sentence: %s" % (t,sentence)
			end = start + len(t)
			currentTokenPosition = end
			locs.append((sentenceStartPos+start,sentenceStartPos+end))
			
		tokenInfo = [ kindred.Token(token,pos,lemma,start,end) for (token,pos),lemma,(start,end) in zip(tokensAndPOS,lemmas,locs) ]
		
		tokens = [ t for t,_ in tokensAndPOS ]
		
		# Get the dependency graph from the parse
		depgraph = [ (i,details['head'],details['rel']) for i,details in depparse.nodes.items() ]
					
		# And we'll filter out any non-existent relations
		depgraph = [ (i,j,rel) for i,j,rel in depgraph if not rel is None and i>0 and j>0 ]
		
		# Remember that parser gives word indices starting from 1, so subtract to keep with starting from 0
		depgraph = [ (i-1,j-1,rel) for i,j,rel in depgraph ]
		
		assert len(depgraph) != 0, "Dependency parse has failed (%d!=0)" % len(depgraph)
		
		#assert len(tokens) == len(depgraph), "Dependency parse has failed (%d!=%d)" % (len(tokens), len(depgraph))
	
		output.append((tokenInfo, depgraph))
	
	return output
	
if __name__ == '__main__':
	text = 'I shot an elephant in my pajamas. The quick brown fox jumped over the lazy dog.'
	
	sentences = sent_tokenize(text)
	sentences = [ word_tokenize(s) for s in sentences ]
	
	taggedsentences = [ pos_tag(tokens) for tokens in sentences ]
	
	#depparser = nltk.parse.malt.MaltParser('maltparser-1.9.0','engmalt.linear-1.7.mco')
	#depparses = depparser.parse_sents(sentences,verbose=False)
	#print(type(depparses), depparses)
	#for d1 in list(depparses):
	#	for d2 in d1:
	#		print([ (i,details['word']) for i,details in d2.nodes.items() ])
		
