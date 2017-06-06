
import sys
import kindred
import requests
import re

from kindred.loadFunctions import parseJSON

def loadPMID(pmid):
	assert isinstance(pmid,int)
	
	annotationsURL = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/%d/JSON" % pmid
	
	annotations = requests.get(annotationsURL).json()
	parsed = parseJSON(annotations)
	
	return parsed

def load(pmids):
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
	
	
	
	
