"""
Importer for PubTator data
"""

import sys
import kindred
import requests
import re

from kindred.loadFunctions import parseJSON

def loadPMID(pmid):
	assert isinstance(pmid,int)
	
	annotationsURL = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/%d/JSON" % pmid
	
	annotations = requests.get(annotationsURL).json()
	doc = parseJSON(annotations)
	
	return doc

def load(pmids):
	"""
	Load a set of documents with annotations from Pubmed given a list of Pubmed IDs (PMIDs)
	
	>>> corpus = load(19894120)
	>>> len(corpus.documents)
	1

	:param pmids: the list of Pubmed IDs (integers)
	:returns: a kindred corpus object
	"""

	assert isinstance(pmids,list) or isinstance(pmids,int)

	corpus = kindred.Corpus()
	if isinstance(pmids,list):
		for pmid in pmids:
			doc = loadPMID(pmid)
			assert isinstance(doc,kindred.Document)
			corpus.addDocument(doc)
	elif isinstance(pmids,int):
		doc = loadPMID(pmids)
		assert isinstance(doc,kindred.Document)
		corpus.addDocument(doc)
	return corpus
	
	
	
	
