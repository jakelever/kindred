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
		m = re.search("sourcedb/(?P<sourcedb>[^\/]*)/sourceid/(?P<sourceid>[0-9]*)",doc['url'])
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
	
	return loaded
	
	
	
