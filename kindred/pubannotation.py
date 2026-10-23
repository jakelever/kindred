"""
Importer for PubAnnotation data
"""

import kindred
import requests
import re

USER_AGENT = 'kindred (https://github.com/jakelever/kindred)'

def _getJSON(url):
	"""
	Fetch a URL from PubAnnotation and parse it as JSON, raising a clear error if it doesn't return JSON (e.g. an error or bot-check page)

	:param url: The URL to fetch
	:type url: str
	:return: The parsed JSON
	:rtype: list or dict
	"""
	response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=60)
	try:
		return response.json()
	except ValueError:
		raise RuntimeError("PubAnnotation did not return JSON for %s (HTTP %d, content type %s)" % (url, response.status_code, response.headers.get('content-type')))

def load(projectName):
	"""
	Download and load the corresponding corpus from the PubAnnotation resource
	
	:param projectName: The name of the PubAnnotation project to download
	:type projectName: str
	:return: The loaded corpus
	:rtype: kindred.Corpus
	"""
	projectURL = "https://pubannotation.org/projects/%s/docs.json" % projectName

	loaded = kindred.Corpus()

	docs = _getJSON(projectURL)
	for doc in docs:
		m = re.search(r"sourcedb/(?P<sourcedb>[^/]*)/sourceid/(?P<sourceid>[0-9]*)",doc['url'])
		mDict = m.groupdict()
		
		assert 'sourcedb' in mDict
		assert 'sourceid' in mDict
		
		annotationsURL = "https://pubannotation.org/projects/%s/docs/sourcedb/%s/sourceid/%s/annotations.json" % (projectName,mDict['sourcedb'],mDict['sourceid'])

		annotations = _getJSON(annotationsURL)
		
		
		assert isinstance(annotations,list) or isinstance(annotations,dict)
		
		if isinstance(annotations,list):
			for annotation in annotations:
				parsed = kindred.loadFunctions.parsePubAnnotationJSON(annotation)
				loaded.addDocument(parsed)
		elif isinstance(annotations,dict):
			parsed = kindred.loadFunctions.parsePubAnnotationJSON(annotations)
			loaded.addDocument(parsed)
	
	return loaded
	
	
	
