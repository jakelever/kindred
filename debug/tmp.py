"""
Importer for PubAnnotation data
"""

import sys
import requests
import re
import time

def check(projectName):
	projectURL = "http://pubannotation.org/projects/%s/docs.json" % projectName
	
	docs = requests.get(projectURL)
	for doc in docs.json():
		print doc['url']
		m = re.search("sourcedb/(?P<sourcedb>[^\/]*)/sourceid/(?P<sourceid>[0-9]*)",doc['url'])
		mDict = m.groupdict()
		
		assert 'sourcedb' in mDict
		assert 'sourceid' in mDict
		
		annotationsURL = "http://pubannotation.org/projects/%s/docs/sourcedb/%s/sourceid/%s/annotations.json" % (projectName,mDict['sourcedb'],mDict['sourceid'])
	#	print annotationsURL
		
		annotations = requests.get(annotationsURL).json()
		
		assert isinstance(annotations,list) or isinstance(annotations,dict)
		
		if isinstance(annotations,list):
			return True
		else:
		 	return False
	
	return False
	
if __name__ == '__main__':
	check('CoGe_Citation_Annotations')

def unused():

	projectListingURL = 'http://pubannotation.org/projects.json'

	projects = requests.get(projectListingURL)
	for project in projects.json():
		print project['name'], 
		sys.stdout.flush()
		print check(project['name'])
		sys.stdout.flush()
		time.sleep(1)
	
