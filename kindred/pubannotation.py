"""
Importer for PubAnnotation data
"""

import kindred
import requests
import re

def load(projectName):
	"""
	Download and load the corresponding corpus from the PubAnnotation resource
	
	:param projectName: The name of the PubAnnotation project to download
	:type projectName: str
	:return: The loaded corpus
	:rtype: kindred.Corpus
	"""
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
				parsed = kindred.loadFunctions.parseJSON(annotation)
				loaded.addDocument(parsed)
		elif isinstance(annotations,dict):
			parsed = kindred.loadFunctions.parseJSON(annotations)
			loaded.addDocument(parsed)
	
	return loaded
	
	
	
