"""
Importer for PubAnnotation data
"""

import sys
import kindred
import requests
import re

from kindred.loadFunctions import parseJSON

def load(projectName):
	projectURL = "http://pubannotation.org/projects/%s/docs.json" % projectName
	
	loaded = kindred.Corpus()
	
	docs = requests.get(projectURL)
	for doc in docs.json():
		m = re.search("sourcedb/(?P<sourcedb>[A-Za-z0-9\-]*)/sourceid/(?P<sourceid>[0-9]*)",doc['url'])
		mDict = m.groupdict()
		
		assert 'sourcedb' in mDict
		assert 'sourceid' in mDict
		
		annotationsURL = "http://pubannotation.org/projects/%s/docs/sourcedb/%s/sourceid/%s/annotations.json" % (projectName,mDict['sourcedb'],mDict['sourceid'])
		
		annotations = requests.get(annotationsURL).json()
		
		
		assert isinstance(annotations,list) or isinstance(annotations,dict)
		
		if isinstance(annotations,list):
			for annotation in annotations:
				parsed = parseJSON(annotation)
				loaded.addDocument(parsed)
		elif isinstance(annotations,dict):
			parsed = parseJSON(annotations)
			loaded.addDocument(parsed)
	
	#sys.exit(0)
	# http://pubannotation.org/projects/example/docs/sourcedb/PubMed/sourceid/25314077/annotations
	# http://pubannotation.org/projects/bionlp-st-ge-2016-reference/docs/sourcedb/PMC/sourceid/1134658/annotations.json
	
	return loaded
	
	
	
