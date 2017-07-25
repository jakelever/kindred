"""
Importer for PubAnnotation data
"""

import sys
import requests
import re
import time
import fileinput

def check(projectName):
	#print projectName
	projectURL = "http://pubannotation.org/projects/%s/docs.json" % projectName
	#print projectURL
	
	docs = requests.get(projectURL)
	return len(list(docs.json()))
	#print docs.json()
	retval = []

	for doc in docs.json():
		print "MOO :", doc
		m = re.search("sourcedb/(?P<sourcedb>[^\/]*)/sourceid/(?P<sourceid>[0-9]*)",doc['url'])
		mDict = m.groupdict()
		
		assert 'sourcedb' in mDict
		assert 'sourceid' in mDict
		
		annotationsURL = "http://pubannotation.org/projects/%s/docs/sourcedb/%s/sourceid/%s/annotations.json" % (projectName,mDict['sourcedb'],mDict['sourceid'])
	#	print annotationsURL
		
		annotations = requests.get(annotationsURL).json()
		
		assert isinstance(annotations,list) or isinstance(annotations,dict)
		
		if isinstance(annotations,list):
			retval.append(len(annotations))
		else:
			retval.append(1)
	
	return retval
	
if __name__ == '__main__':
	#projectListingURL = 'http://pubannotation.org/projects.json'

	#projects = requests.get(projectListingURL)
	#for project in projects.json():
	for projectName in fileinput.input():
		projectName = projectName.strip()
		print projectName.encode('utf8'), 
		sys.stdout.flush()
		print check(projectName)
		sys.stdout.flush()
		time.sleep(1)
	
