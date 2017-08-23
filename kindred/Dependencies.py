
import kindred

import os
import subprocess
import shlex
import time
import atexit
import tempfile
import requests
import pytest_socket
import sys
import shutil

homeDirectory = os.path.expanduser('~')
downloadDirectory = os.path.join(homeDirectory,'.kindred')
	
corenlpProcess = None
stdoutFile = None
stderrFile = None

currentCoreNLPInfo = {'url':'http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip','archive':'stanford-corenlp-full-2017-06-09.zip','directory':'stanford-corenlp-full-2017-06-09','sha256':'7fb27a0e8dd39c1a90e4155c8f27cd829956e8b8ec6df76b321c04b1fe887961'}

def killCoreNLP():
	global corenlpProcess
	global stdoutFile
	global stderrFile
	if not corenlpProcess is None:
		corenlpProcess.kill()
		stdoutFile.close()
		stderrFile.close()

		corenlpProcess = None
		stdoutFile = None
		stderrFile = None

def checkCoreNLPDownload():
	corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
	return not corenlpDir is None

def hasOldCoreNLP():
	for root, dirs, files in os.walk(downloadDirectory):
		for dirName in dirs:
			if dirName.startswith('stanford-corenlp') and not dirName == currentCoreNLPInfo['directory']:
				return True
	return False

def deleteOldCoreNLP():
	filesToDelete = []
	for root, dirs, files in os.walk(downloadDirectory):
		for fileName in files:
			if fileName.startswith('stanford-corenlp') and fileName.endswith('.zip'):
				fullPath = os.path.join(root,fileName)
				filesToDelete.append(fullPath)

	directoriesToDelete = []
	for root, dirs, files in os.walk(downloadDirectory):
		for dirName in dirs:
			if dirName.startswith('stanford-corenlp') and not dirName == currentCoreNLPInfo['directory']:
				fullPath = os.path.join(root,dirName)
				directoriesToDelete.append(fullPath)

	for fileToDelete in filesToDelete:
		if os.path.isfile(fileToDelete):
			os.remove(fileToDelete)

	for directoryToDelete in directoriesToDelete:
		if os.path.isdir(directoryToDelete):
			shutil.rmtree(directoryToDelete)

def downloadCoreNLP():
	"""
	Download the files necessary to run Stanford CoreNLP
	"""
	deleteOldCoreNLP()

	global downloadDirectory
	corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
	if corenlpDir is None:
		files = []
		files.append((currentCoreNLPInfo['url'],currentCoreNLPInfo['archive'],currentCoreNLPInfo['sha256']))
		
		print("Downloading CoreNLP to %s" % downloadDirectory)
		sys.stdout.flush()
		kindred.utils._downloadFiles(files,downloadDirectory)
		corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
		assert not corenlpDir is None, "Error after downloading, could not find corenlp directory"
		print ("Download complete.")
	else:
		print ("CoreNLP is already downloaded. No need to download")

def getCoreNLPLanguageFileInfo(language):
	acceptedLanguages = ['arabic','chinese','english','french','german','spanish']
	assert language in acceptedLanguages

	files = {}
	files['arabic'] = ('http://nlp.stanford.edu/software/stanford-arabic-corenlp-2017-06-09-models.jar','stanford-arabic-corenlp-2017-06-09-models.jar','c6268790563371afa6b57d1b3ae69d94e6c41da4c1242bbc606fa3b1e00c84a2')
	files['chinese'] = ('http://nlp.stanford.edu/software/stanford-chinese-corenlp-2017-06-09-models.jar','stanford-chinese-corenlp-2017-06-09-models.jar','56ed3b9d750b89e0dea241311573a6ee8d5ae1b9edf7dda94716dd212f042977')
	files['french'] = ('http://nlp.stanford.edu/software/stanford-french-corenlp-2017-06-09-models.jar','stanford-french-corenlp-2017-06-09-models.jar','d726e8fec6440448d195b4e7b10e7fe8abef3f3274059af614675507331b5fed')
	files['german'] = ('http://nlp.stanford.edu/software/stanford-german-corenlp-2017-06-09-models.jar','stanford-german-corenlp-2017-06-09-models.jar','1febe0aeb2bc4da8cd67cdbb49594329fac58b3b7a699bfd8cc7a13b001ab9c2')
	files['spanish'] = ('http://nlp.stanford.edu/software/stanford-spanish-corenlp-2017-06-09-models.jar','stanford-spanish-corenlp-2017-06-09-models.jar','302d8d0f1e4220b9a05fe333db531b899a9983c7ac22f5d71588cd7250762123')

	return files[language]

def coreNLPLanguageFileExists(language):
	acceptedLanguages = ['arabic','chinese','french','german','spanish']
	assert language in acceptedLanguages

	corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
	expectedBasename = getCoreNLPLanguageFileInfo(language)[1]
	expectedFullname = os.path.join(corenlpDir,expectedBasename)

	return os.path.isfile(expectedFullname)

def downloadCoreNLPLanguage(language):
	"""
	Download a language model for Stanford CoreNLP

	:param language: The language to download (arabic/chinese/french/german/spanish). English does not need to be downloaded (as it comes as default in CoreNLP)
	:type language: str
	"""

	acceptedLanguages = ['arabic','chinese','french','german','spanish']
	assert language in acceptedLanguages

	corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
	kindred.utils._downloadFiles([getCoreNLPLanguageFileInfo(language)],corenlpDir)

	assert coreNLPLanguageFileExists(language), 'Error downloading CoreNLP language file'


def testCoreNLPConnection():
	try:
		requests.get('http://localhost:9000')
		return True
	except requests.exceptions.ConnectionError:
		return False
	except pytest_socket.SocketBlockedError:
		return False



def initializeCoreNLP(language='english'):
	"""
	Launch a local instance of Stanford CoreNLP (assuming the files have already been downloaded)

	:param language: The language that the CoreNLP instance should use (english/arabic/chinese/french/german/spanish).
	:type language: str
	"""
	global corenlpProcess
	global stdoutFile
	global stderrFile

	acceptedLanguages = ['english','arabic','chinese','french','german','spanish']
	assert language in acceptedLanguages



	if testCoreNLPConnection():
		return

	if hasOldCoreNLP():
		raise RuntimeError("Kindred needs a newer version of CoreNLP. Please use kindred.downloadCoreNLP() to upgrade to the latest version (and clear out the old version)")

	corenlpDir = kindred.utils._findDir(currentCoreNLPInfo['directory'],downloadDirectory)
	if corenlpDir is None:
		raise RuntimeError("Unable to find local server so trying to initialize CoreNLP instance. Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first if subprocess should be used.")

	if language != 'english' and not coreNLPLanguageFileExists(language):
		raise RuntimeError("Could not find the Stanford CoreNLP model files for language: %s. Use kindred.downloadCoreNLPLanguage('%s') first." % (language,language))

	if language == 'english':
		command='java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 150000'
	else:
		command='java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-%s.properties -port 9000 -timeout 150000' % language

	os.chdir(corenlpDir)

	stdoutFile = tempfile.NamedTemporaryFile(delete=True)
	stderrFile = tempfile.NamedTemporaryFile(delete=True)

	corenlpProcess = subprocess.Popen(shlex.split(command), stdout=stdoutFile, stderr=stderrFile, cwd=corenlpDir)#, shell=True)

	atexit.register(killCoreNLP)

	maxTries = 10

	connectionSuccess = False
	for tries in range(maxTries):
		if testCoreNLPConnection():
			connectionSuccess = True
			break
		time.sleep(5)

	if not connectionSuccess:
		killCoreNLP()
		raise RuntimeError("Unable to connect to launched CoreNLP subprocess")

	time.sleep(1)
		
