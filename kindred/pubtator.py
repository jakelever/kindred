"""
Importer for PubTator data
"""

import kindred
import requests
import json
import time
import io
import bioc

def _loadPMID(pmid,retries=3):
	assert isinstance(pmid,int)
	
	annotationsURL = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocxml?pmids=%d" % pmid

	success = False
	for retry in range(retries):
		try:
			request = requests.get(annotationsURL)
			annotations = request.text
			success = True
			break
		except ValueError as e:
		 	time.sleep(1)

	if not success:
		raise RuntimeError('Unable to download PubTator data after %d retries' % retries)

	collection = bioc.load(io.BytesIO(annotations.encode()))
	assert isinstance(collection,bioc.BioCCollection)
	assert len(collection.documents) == 1
	
	documents = kindred.loadFunctions.convertBiocDocToKindredDocs(collection.documents[0])

	return documents

def load(pmids):
	"""
	Load a set of documents with annotations from Pubmed given a list of Pubmed IDs (PMIDs)
	
	>>> corpus = load(19894120)
	>>> len(corpus.documents)
	1

	:param pmids: the list of Pubmed IDs
	:type pmids: List of ints
	:returns: a kindred corpus object
	:rtype: kindred.Corpus
	"""

	assert isinstance(pmids,list) or isinstance(pmids,int)

	corpus = kindred.Corpus()
	if isinstance(pmids,list):
		for pmid in pmids:
			corpus.documents += _loadPMID(pmid)
	elif isinstance(pmids,int):
		corpus.documents = _loadPMID(pmids)
	return corpus
	

