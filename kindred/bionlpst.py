"""
Importer for BioNLP Shared Task data
"""

import os
import tempfile
import sys
import shutil
import six

import kindred

# Load the task information into this data structure
taskOptions = {}
bionlpstFile = os.path.join(os.path.dirname(__file__),'bionlpst_files.txt')
with open(bionlpstFile,'r') as f:
	for line in f:
		if line.strip() != '':
			taskName,url,expectedFile,expectedSHA256 = line.strip().split('\t')
			taskOptions[taskName] = (url,expectedFile,expectedSHA256)

def listTasks():
	"""
	List the names of the BioNLP Shared Task datasets that can be loaded. These values can be passed to the kindred.bionlpst.load function as the taskName argument

	:return: List of valid taskNames
	:rtype: str
	"""
	
	return sorted(list(taskOptions.keys()))

def load(taskName,ignoreEntities=[]):
	"""
	Download and load the corresponding corpus from the BioNLP Shared Task
	
	:param taskName: The name of the shared task to download (e.g. 'BioNLP-ST-2016_BB-event_train'). Use kindred.bionlpst.listTasks() to get a list of valid options
	:param ignoreEntities: A list of any entities that should be ignored during loading
	:type taskName: str
	:type ignoreEntities: list of str
	:return: The loaded corpus
	:rtype: kindred.Corpus
	"""
	global taskOptions

	tempDir = tempfile.mkdtemp()

	assert taskName in taskOptions.keys(), "%s not a valid option in %s" % (taskName, taskOptions.keys())
	url,expectedFile,expectedSHA256 = taskOptions[taskName]
	filesToDownload = [(url,expectedFile,expectedSHA256)]
	expectedDir = expectedFile.replace('.zip','')

	try:
		kindred.utils._downloadFiles(filesToDownload,tempDir)
	except:
		exc_info = sys.exc_info()
		shutil.rmtree(tempDir)
		six.reraise(*exc_info)

	mainDir = kindred.utils._findDir(expectedDir,tempDir)

	corpus = kindred.loadDir(dataFormat='standoff',directory=mainDir,ignoreEntities=ignoreEntities)

	shutil.rmtree(tempDir)

	return corpus

